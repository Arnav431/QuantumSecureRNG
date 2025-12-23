from qiskit_ibm_runtime import QiskitRuntimeService
import hashlib

def quantum_bits_from_job(job_id):
    """
    Extract random bits from a completed IBM Quantum job.
    
    Args:
        job_id: The IBM Quantum job ID
        
    Returns:
        str: Concatenated bitstring from measurement results
    """
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
    job = service.job(job_id)
    result = job.result()
    
    # Handle different result formats
    counts = None
    
    # Method 0: Direct dictionary format (legacy or raw results)
    if isinstance(result, dict):
        # Try common dictionary keys for counts
        if 'counts' in result:
            counts = result['counts']
        elif 'quasi_dists' in result:
            # Convert quasi_dists to counts
            quasi_dist = result['quasi_dists']
            if isinstance(quasi_dist, list) and len(quasi_dist) > 0:
                quasi_dist = quasi_dist[0]
            counts = {format(int(key), 'b'): int(prob * 1024) 
                     for key, prob in quasi_dist.items()}
        elif 'results' in result:
            # Nested results structure
            nested = result['results']
            
            if isinstance(nested, list):
                if len(nested) > 0:
                    nested = nested[0]
            
            if isinstance(nested, dict):
                if 'data' in nested:
                    data = nested['data']
                    
                    # Check what 'c' contains
                    if 'c' in data:
                        c_data = data['c']
                        
                        # If c is a dict-like object with counts
                        if isinstance(c_data, dict):
                            counts = c_data
                        # If c has a get_counts method
                        elif hasattr(c_data, 'get_counts'):
                            counts = c_data.get_counts()
                        # If c is a list of measurements
                        elif isinstance(c_data, list):
                            counts = {}
                            for bitstring in c_data:
                                bitstring = str(bitstring)
                                counts[bitstring] = counts.get(bitstring, 0) + 1
                    
                    if counts is None and 'counts' in data:
                        counts = data['counts']
                    elif counts is None and 'memory' in data:
                        # Convert memory to counts
                        memory = data['memory']
                        counts = {}
                        for bitstring in memory:
                            counts[bitstring] = counts.get(bitstring, 0) + 1
                elif 'counts' in nested:
                    # counts might be directly in results[0]
                    counts = nested['counts']
                elif 'header' in nested and 'memory' in nested:
                    # Another common format
                    memory = nested['memory']
                    counts = {}
                    for bitstring in memory:
                        counts[bitstring] = counts.get(bitstring, 0) + 1
        # If dict looks like counts itself (bitstring keys)
        elif all(isinstance(k, str) and all(c in '01' for c in k) for k in list(result.keys())[:5]):
            counts = result
    
    # Method 1: Try Sampler V2 format (PrimitiveResult with PubResult)
    if counts is None:
        try:
            if hasattr(result, '__len__') and len(result) > 0:
                pub_result = result[0]
                if hasattr(pub_result, 'data'):
                    if hasattr(pub_result.data, 'meas'):
                        counts = pub_result.data.meas.get_counts()
                    elif hasattr(pub_result.data, 'c'):
                        counts = pub_result.data.c.get_counts()
        except (AttributeError, IndexError, KeyError, TypeError):
            pass
    
    # Method 2: Try direct get_counts (Sampler V1 or legacy)
    if counts is None:
        try:
            if hasattr(result, 'get_counts'):
                counts = result.get_counts()
        except (AttributeError, TypeError):
            pass
    
    # Method 3: Try quasi_dists (another V2 format)
    if counts is None:
        try:
            if hasattr(result, 'quasi_dists') and len(result.quasi_dists) > 0:
                # Convert quasi_dists to counts-like format
                quasi_dist = result.quasi_dists[0]
                counts = {format(key, 'b'): int(prob * 1024) 
                         for key, prob in quasi_dist.items()}
        except (AttributeError, IndexError, KeyError, TypeError):
            pass
    
    # Method 4: Check if result is directly iterable with metadata
    if counts is None:
        try:
            for pub_result in result:
                if hasattr(pub_result, 'data'):
                    data = pub_result.data
                    # Try all common attribute names
                    for attr_name in ['meas', 'c', 'counts', 'cr']:
                        if hasattr(data, attr_name):
                            attr = getattr(data, attr_name)
                            if hasattr(attr, 'get_counts'):
                                counts = attr.get_counts()
                                break
                if counts:
                    break
        except (TypeError, AttributeError):
            pass
    
    if counts is None:
        raise RuntimeError(
            f"Failed to extract counts from job result. "
            f"Result type: {type(result)}. "
            f"Please check the job type and result format."
        )
    
    # Validate counts format
    if not counts or not isinstance(counts, dict):
        raise ValueError(f"Invalid counts format: {counts}")
    
    # Handle two different count formats
    bits = ""
    
    # Format 1: {'samples': [...], 'num_bits': N} - list of hex measurements
    if 'samples' in counts and 'num_bits' in counts:
        samples = counts['samples']
        num_bits = counts['num_bits']
        print(f"[+] Processing {len(samples)} samples with {num_bits} bits each")
        
        for hex_val in samples:
            # Convert hex string (e.g., '0xa') to binary string (e.g., '1010')
            decimal = int(hex_val, 16)
            binary = format(decimal, f'0{num_bits}b')  # Pad to num_bits width
            bits += binary
    
    # Format 2: {'bitstring': frequency} - standard counts dictionary
    elif all(isinstance(v, int) for v in counts.values()):
        for bitstring, freq in sorted(counts.items()):
            bits += str(bitstring) * freq
    
    else:
        raise ValueError(f"Unrecognized counts format: {counts}")
    
    print(f"[+] Extracted {len(bits)} total bits")
    return bits


def validate_quantum_bits(bits):
    """Validate quantum bits have reasonable entropy"""
    if len(bits) < 256:
        raise ValueError(f"Insufficient entropy: only {len(bits)} bits")
    
    ones = bits.count('1')
    ratio = ones / len(bits) if len(bits) > 0 else 0
    
    if ratio < 0.3 or ratio > 0.7:
        raise ValueError(f"Suspicious bias detected: {ratio:.1%} ones")
    
    print(f"[+] Quantum bits validated: {len(bits)} bits, {ratio:.1%} ones")
    return True


def get_quantum_entropy(job_id, num_bytes=32):
    """
    Get cryptographically suitable random bytes from quantum measurements.
    
    Args:
        job_id: The IBM Quantum job ID
        num_bytes: Number of random bytes to generate (default 32 for AES-256)
        
    Returns:
        bytes: Cryptographic-quality random bytes
    """
    raw_bits = quantum_bits_from_job(job_id)
    validate_quantum_bits(raw_bits)
    
    # Apply SHA-256 as a randomness extractor to remove bias
    hashed = hashlib.sha256(raw_bits.encode()).digest()
    
    # If you need more than 32 bytes, you could chain hashes or use HKDF
    return hashed[:num_bytes]