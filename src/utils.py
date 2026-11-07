"""
Utility functions for sequence I/O and external API integration.

- FASTA file parsing
- Sequence validation
- UniProtKB API queries (AC/ID → sequence)
"""

import re
from typing import Optional, Tuple, List
import requests


# UniProtKB REST API base
UNIPROT_API = "https://rest.uniprot.org/uniprotkb"


def parse_fasta(fasta_text: str) -> Tuple[str, str]:
    """
    Parse FASTA format and return (header, sequence).

    Args:
        fasta_text: FASTA text (may contain multiple lines, whitespace, etc.)

    Returns:
        Tuple of (header, sequence)

    Raises:
        ValueError: If format is invalid (no '>', empty sequence)

    Example:
        >>> parse_fasta(">sp|P12345|ABC_HUMAN\\nMVLSPA\\nDKTNVI")
        ('sp|P12345|ABC_HUMAN', 'MVLSPADKTOVI')
    """
    lines = fasta_text.strip().split('\n')

    if not lines or not lines[0].startswith('>'):
        raise ValueError("FASTA must start with '>' (header line)")

    header = lines[0][1:].strip()  # Remove '>'
    sequence = ''.join(line.strip() for line in lines[1:] if line.strip())

    if not sequence:
        raise ValueError("FASTA sequence is empty")

    return header, sequence


def parse_fasta_file(filepath: str) -> List[Tuple[str, str]]:
    """
    Parse FASTA file (may contain multiple records).

    Args:
        filepath: Path to FASTA file

    Returns:
        List of (header, sequence) tuples

    Raises:
        FileNotFoundError: If file not found
        ValueError: If FASTA format invalid
    """
    records = []
    current_header = None
    current_seq = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # Save previous record
                if current_header is not None:
                    seq = ''.join(current_seq)
                    if seq:
                        records.append((current_header, seq))
                # Start new record
                current_header = line[1:].strip()
                current_seq = []
            elif line and current_header is not None:
                current_seq.append(line)

        # Save last record
        if current_header is not None:
            seq = ''.join(current_seq)
            if seq:
                records.append((current_header, seq))

    if not records:
        raise ValueError("No valid FASTA records found in file")

    return records


def is_uniprot_ac(identifier: str) -> bool:
    """
    Check if identifier looks like UniProtKB Accession (AC).

    UniProtKB AC format: [A-Z][A-Z0-9]{5} (e.g., P12345, Q9Y5K6)
    """
    return bool(re.match(r'^[A-Z][A-Z0-9]{5}$', identifier))


def is_uniprot_id(identifier: str) -> bool:
    """
    Check if identifier looks like UniProtKB ID (Entry name).

    Example: ABC_HUMAN, TP53_HUMAN (format: NAME_ORGANISM)
    """
    return bool(re.match(r'^[A-Z0-9]+_[A-Z0-9]+$', identifier))


def query_uniprot_sequence(identifier: str, timeout: int = 10) -> Tuple[str, dict]:
    """
    Query UniProtKB for sequence by AC or ID.

    Args:
        identifier: UniProtKB AC (e.g., P12345) or ID (e.g., TP53_HUMAN)
        timeout: Request timeout in seconds

    Returns:
        Tuple of (sequence, metadata_dict)
        metadata includes: accession, id, organism, length, entry_type

    Raises:
        ValueError: If identifier format invalid
        requests.RequestException: If API query fails
        LookupError: If entry not found
    """
    if not (is_uniprot_ac(identifier) or is_uniprot_id(identifier)):
        raise ValueError(
            f"Invalid UniProtKB identifier: {identifier}. "
            f"Expected AC (P12345) or ID (ABC_HUMAN)"
        )

    try:
        # Query UniProtKB REST API
        url = f"{UNIPROT_API}/{identifier}.json"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        entry = data.get('entryType', 'Unknown')

        # Extract sequence
        sequence_data = data.get('sequence', {})
        sequence = sequence_data.get('value', '')

        if not sequence:
            raise LookupError(f"No sequence found for {identifier}")

        # Extract metadata
        metadata = {
            'accession': data.get('primaryAccession', identifier),
            'id': data.get('uniProtkbId', 'Unknown'),
            'organism': 'Unknown',
            'length': sequence_data.get('length', len(sequence)),
            'entry_type': entry,
        }

        # Try to extract organism
        for org_ref in data.get('organism', []):
            if org_ref.get('scientificName'):
                metadata['organism'] = org_ref['scientificName']
                break

        return sequence, metadata

    except requests.exceptions.RequestException as e:
        raise requests.RequestException(
            f"Failed to query UniProtKB for {identifier}: {e}"
        )


def detect_sequence_format(text: str) -> str:
    """
    Auto-detect input sequence format.

    Returns:
        One of: "fasta", "uniprot_ac", "uniprot_id", "raw"

    Examples:
        ">sp|P123|ABC" → "fasta"
        "P12345" → "uniprot_ac"
        "TP53_HUMAN" → "uniprot_id"
        "MVLSPADKTOV" → "raw"
    """
    text = text.strip()

    if text.startswith('>'):
        return "fasta"
    elif is_uniprot_ac(text):
        return "uniprot_ac"
    elif is_uniprot_id(text):
        return "uniprot_id"
    else:
        return "raw"


def load_sequence(
    sequence_input: str,
    query_uniprot: bool = True,
    timeout: int = 10
) -> Tuple[str, dict]:
    """
    Load protein sequence from various input formats.

    Args:
        sequence_input: FASTA text, UniProtKB AC/ID, or raw sequence
        query_uniprot: If True, query UniProtKB for AC/ID inputs
        timeout: Request timeout (seconds)

    Returns:
        Tuple of (sequence, metadata)

    Raises:
        ValueError: If input format invalid or sequence empty
        LookupError: If UniProtKB query fails
    """
    fmt = detect_sequence_format(sequence_input)

    if fmt == "fasta":
        header, seq = parse_fasta(sequence_input)
        return seq, {"source": "fasta", "header": header}

    elif fmt in ("uniprot_ac", "uniprot_id"):
        if query_uniprot:
            try:
                seq, meta = query_uniprot_sequence(sequence_input, timeout=timeout)
                meta['source'] = 'uniprot'
                meta['query'] = sequence_input
                return seq, meta
            except (requests.RequestException, LookupError) as e:
                raise LookupError(f"UniProtKB query failed: {e}")
        else:
            raise ValueError(
                f"UniProtKB queries disabled. Got {fmt} identifier: {sequence_input}"
            )

    elif fmt == "raw":
        # Treat as raw amino acid sequence
        return sequence_input, {"source": "raw"}

    else:
        raise ValueError(f"Unknown sequence format: {fmt}")


if __name__ == "__main__":
    # Example 1: Parse FASTA
    fasta_ex = ">sp|P12345|ABC_HUMAN\nMVLSPADKTNVI\nRAA"
    header, seq = parse_fasta(fasta_ex)
    print(f"FASTA example: header={header}, seq={seq}\n")

    # Example 2: Detect format
    for test_input in [
        ">sp|P123|ABC",
        "P12345",
        "TP53_HUMAN",
        "MVLSPADKTVI"
    ]:
        fmt = detect_sequence_format(test_input)
        print(f"  '{test_input}' → {fmt}")

    # Example 3: UniProtKB query (disabled by default for testing)
    # seq, meta = query_uniprot_sequence("P12345")
    # print(f"\nUniProtKB query: {meta}")
