def signal_samples_are_equal(file_name, samples):
    expected_indices = []
    expected_samples = []
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            lx = line.strip()
            if len(lx.split(' ')) == 2:
                lx = line.split(' ')
                v1 = int(lx[0])
                v2 = float(lx[1])
                expected_indices.append(v1)
                expected_samples.append(v2)
                line = f.readline()
            else:
                break

    if len(expected_samples) != len(samples):

        return "Test case failed, your signal have different length from the expected one"

    for i in range(len(expected_samples)):
        if abs(samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            return "Test case failed, your signal have different values from the expected one"

    return "Test case passed successfully"
