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
    

    counts = None
    

    if isinstance(result, dict):

        if 'counts' in result:
            counts = result['counts']
        elif 'quasi_dists' in result:

            quasi_dist = result['quasi_dists']
            if isinstance(quasi_dist, list) and len(quasi_dist) > 0:
                quasi_dist = quasi_dist[0]
            counts = {format(int(key), 'b'): int(prob * 1024) 
                     for key, prob in quasi_dist.items()}
        elif 'results' in result:

            nested = result['results']
            
            if isinstance(nested, list):
                if len(nested) > 0:
                    nested = nested[0]
            
            if isinstance(nested, dict):
                if 'data' in nested:
                    data = nested['data']
                    

                    if 'c' in data:
                        c_data = data['c']
                        
                        if isinstance(c_data, dict):
                            counts = c_data

                        elif hasattr(c_data, 'get_counts'):
                            counts = c_data.get_counts()
                        elif isinstance(c_data, list):
                            counts = {}
                            for bitstring in c_data:
                                bitstring = str(bitstring)
                                counts[bitstring] = counts.get(bitstring, 0) + 1
                    
                    if counts is None and 'counts' in data:
                        counts = data['counts']
                    elif counts is None and 'memory' in data:
                        memory = data['memory']
                        counts = {}
                        for bitstring in memory:
                            counts[bitstring] = counts.get(bitstring, 0) + 1
                elif 'counts' in nested:
                    counts = nested['counts']
                elif 'header' in nested and 'memory' in nested:
                    memory = nested['memory']
                    counts = {}
                    for bitstring in memory:
                        counts[bitstring] = counts.get(bitstring, 0) + 1
        elif all(isinstance(k, str) and all(c in '01' for c in k) for k in list(result.keys())[:5]):
            counts = result
    

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
    
    if counts is None:
        try:
            if hasattr(result, 'get_counts'):
                counts = result.get_counts()
        except (AttributeError, TypeError):
            pass

    if counts is None:
        try:
            if hasattr(result, 'quasi_dists') and len(result.quasi_dists) > 0:

                quasi_dist = result.quasi_dists[0]
                counts = {format(key, 'b'): int(prob * 1024) 
                         for key, prob in quasi_dist.items()}
        except (AttributeError, IndexError, KeyError, TypeError):
            pass

    if counts is None:
        try:
            for pub_result in result:
                if hasattr(pub_result, 'data'):
                    data = pub_result.data

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
    
    if not counts or not isinstance(counts, dict):
        raise ValueError(f"Invalid counts format: {counts}")
    

    bits = ""
    

    if 'samples' in counts and 'num_bits' in counts:
        samples = counts['samples']
        num_bits = counts['num_bits']
        print(f"[+] Processing {len(samples)} samples with {num_bits} bits each")
        
        for hex_val in samples:

            decimal = int(hex_val, 16)
            binary = format(decimal, f'0{num_bits}b')
            bits += binary
    

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
    

    hashed = hashlib.sha256(raw_bits.encode()).digest()
    
    return hashed[:num_bytes]