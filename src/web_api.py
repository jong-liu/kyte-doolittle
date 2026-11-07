"""
FastAPI backend for Kyte-Doolittle hydropathy scale calculator.

Endpoints:
  POST /api/calculate — Calculate hydropathy scores
  GET /api/health — Health check
  POST /api/batch — Batch processing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from kyte_doolittle import calculate_hydropathy, validate_sequence
from utils import load_sequence, detect_sequence_format


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kyte–Doolittle Hydropathy Scale API",
    description="Calculate protein hydropathy profiles using the Kyte-Doolittle method (1982)",
    version="0.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Request/Response Models ============

class CalculateRequest(BaseModel):
    """Request body for hydropathy calculation."""
    sequence: str = Field(..., description="Protein sequence (FASTA, UniProtKB AC/ID, or raw)")
    window_size: int = Field(default=9, ge=3, le=21, description="Sliding window size (odd number)")
    edge_weight: float = Field(default=100, ge=0, le=100, description="Window edge weight (%)")
    weight_model: str = Field(default="linear", pattern="^(linear|exponential)$")
    normalize: bool = Field(default=False, description="Normalize scores to 0-1")
    query_uniprot: bool = Field(default=True, description="Query UniProtKB for AC/ID")

    class Config:
        json_schema_extra = {
            "example": {
                "sequence": ">sp|P12345|ABC_HUMAN\nMVLSPADKTNVI",
                "window_size": 9,
                "edge_weight": 100,
                "weight_model": "linear",
                "normalize": False,
                "query_uniprot": True
            }
        }


class HydropathyMetadata(BaseModel):
    """Metadata about the calculation."""
    sequence_length: int
    window_size: int
    edge_weight: float
    weight_model: str
    normalize: bool
    min: float
    max: float
    mean: float
    std: float


class CalculateResponse(BaseModel):
    """Response body for hydropathy calculation."""
    scores: List[float] = Field(..., description="Hydropathy score at each position")
    metadata: HydropathyMetadata
    sequence_source: str = Field(..., description="Source format: fasta, uniprot, raw")
    sequence_id: Optional[str] = Field(None, description="UniProtKB AC/ID if queried")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# ============ Endpoints ============

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/calculate", response_model=CalculateResponse)
async def calculate_hydropathy_endpoint(req: CalculateRequest):
    """
    Calculate hydropathy scores for a protein sequence.

    Accepts:
    - FASTA format: ">header\\nMVLSPA..."
    - UniProtKB AC: "P12345"
    - UniProtKB ID: "TP53_HUMAN"
    - Raw sequence: "MVLSPADKTVI..."

    Returns:
    - Hydropathy scores (position by position)
    - Statistics (min, max, mean, std)
    - Sequence metadata

    Example request:
    ```
    POST /api/calculate
    {
      "sequence": "MVLSPADKTNVI",
      "window_size": 9,
      "edge_weight": 100,
      "weight_model": "linear",
      "normalize": false
    }
    ```
    """
    try:
        # Load sequence from various formats
        sequence, seq_metadata = load_sequence(
            req.sequence,
            query_uniprot=req.query_uniprot,
            timeout=10
        )

        # Validate sequence
        validated_seq = validate_sequence(sequence)

        # Check window size validity
        if req.window_size % 2 == 0 or req.window_size < 3 or req.window_size > 21:
            raise ValueError("window_size must be odd and between 3-21")

        # Calculate hydropathy
        scores, metadata = calculate_hydropathy(
            validated_seq,
            window_size=req.window_size,
            edge_weight=req.edge_weight,
            weight_model=req.weight_model,
            normalize=req.normalize
        )

        return CalculateResponse(
            scores=scores,
            metadata=HydropathyMetadata(**metadata),
            sequence_source=seq_metadata.get('source', 'unknown'),
            sequence_id=seq_metadata.get('accession') or seq_metadata.get('query')
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except LookupError as e:
        logger.error(f"UniProtKB lookup error: {e}")
        raise HTTPException(status_code=404, detail=f"Sequence not found: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/api/batch")
async def batch_calculate(requests: List[CalculateRequest]):
    """
    Batch process multiple sequences.

    Args:
        requests: List of CalculateRequest objects

    Returns:
        List of CalculateResponse objects
    """
    results = []
    for req in requests:
        try:
            result = await calculate_hydropathy_endpoint(req)
            results.append({"status": "success", "result": result})
        except HTTPException as e:
            results.append({"status": "error", "error": e.detail})
    return results


# ============ Startup / Shutdown ============

@app.on_event("startup")
async def startup_event():
    """Log startup."""
    logger.info("Kyte–Doolittle API server started")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown."""
    logger.info("Kyte–Doolittle API server stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
