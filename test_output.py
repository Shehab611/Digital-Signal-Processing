def signal_samples_are_equal(file_name, samples):
    expected_indices = []
    expected_samples = []
    with open(file_name, 'r') as f:
        f.readline()
        f.readline()
        f.readline()
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


def QuantizationTest1(file_name, Your_EncodedValues, Your_QuantizedValues):
    expectedEncodedValues = []
    expectedQuantizedValues = []
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L = line.strip()
            if len(L.split(' ')) == 2:
                L = line.split(' ')
                V2 = str(L[0])
                V3 = float(L[1])
                expectedEncodedValues.append(V2)
                expectedQuantizedValues.append(V3)
                line = f.readline()
            else:
                break
    if ((len(Your_EncodedValues) != len(expectedEncodedValues)) or (
            len(Your_QuantizedValues) != len(expectedQuantizedValues))):

        print(f"{len(Your_EncodedValues)}  ==>  {len(expectedEncodedValues)}")
        print(f"{len(Your_QuantizedValues)}  ==>  {len(expectedQuantizedValues)}")

        return "QuantizationTest1 Test case failed, your signal have different length from the expected one"

    for i in range(len(Your_EncodedValues)):
        if Your_EncodedValues[i] != expectedEncodedValues[i]:
            return ("QuantizationTest1 Test case failed, your EncodedValues have different EncodedValues from the "
                    "expected one")

    for i in range(len(expectedQuantizedValues)):
        if abs(Your_QuantizedValues[i] - expectedQuantizedValues[i]) < 0.01:
            continue
        else:
            return ("QuantizationTest1 Test case failed, your QuantizedValues have different values from the expected "
                    "one")

    return "QuantizationTest1 Test case passed successfully"


def QuantizationTest2(file_name, Your_IntervalIndices, Your_EncodedValues, Your_QuantizedValues, Your_SampledError):
    expectedIntervalIndices = []
    expectedEncodedValues = []
    expectedQuantizedValues = []
    expectedSampledError = []
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L = line.strip()
            if len(L.split(' ')) == 4:
                L = line.split(' ')
                V1 = int(L[0])
                V2 = str(L[1])
                V3 = float(L[2])
                V4 = float(L[3])
                expectedIntervalIndices.append(V1)
                expectedEncodedValues.append(V2)
                expectedQuantizedValues.append(V3)
                expectedSampledError.append(V4)
                line = f.readline()
            else:
                break
    if (len(Your_IntervalIndices) != len(expectedIntervalIndices)
            or len(Your_EncodedValues) != len(expectedEncodedValues)
            or len(Your_QuantizedValues) != len(expectedQuantizedValues)
            or len(Your_SampledError) != len(expectedSampledError)):
        print(f"{len(Your_IntervalIndices)}  ==>  {len(expectedIntervalIndices)}")
        print(f"{len(Your_EncodedValues)}  ==>  {len(expectedEncodedValues)}")
        print(f"{len(Your_QuantizedValues)}  ==>  {len(expectedQuantizedValues)}")
        print(f"{len(Your_SampledError)}  ==>  {len(expectedSampledError)}")
        return "QuantizationTest2 Test case failed, your signal have different length from the expected one"

    for i in range(len(Your_IntervalIndices)):
        if Your_IntervalIndices[i] != expectedIntervalIndices[i]:
            return "QuantizationTest2 Test case failed, your signal have different indicies from the expected one"

    for i in range(len(Your_EncodedValues)):
        if Your_EncodedValues[i] != expectedEncodedValues[i]:
            return (
                "QuantizationTest2 Test case failed, your EncodedValues have different EncodedValues from the "
                "expected one")

    for i in range(len(expectedQuantizedValues)):
        if abs(Your_QuantizedValues[i] - expectedQuantizedValues[i]) < 0.01:
            continue
        else:
            return (
                "QuantizationTest2 Test case failed, your QuantizedValues have different values from the expected one")

    for i in range(len(expectedSampledError)):
        if abs(Your_SampledError[i] - expectedSampledError[i]) < 0.01:
            continue
        else:
            return "QuantizationTest2 Test case failed, your SampledError have different values from the expected one"

    return "QuantizationTest2 Test case passed successfully"
