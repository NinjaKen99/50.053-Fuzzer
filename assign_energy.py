def AssignEnergy(input_data: dict):
    complexity = 0
    
    for key, value in input_data.items():
        complexity += len(str(value))
    
    # This is a simple proportional assignment; adjust the divisor as needed
    energy = max(1, complexity // 10)  # Ensure at least 1 energy unit is assigned
    
    return energy
