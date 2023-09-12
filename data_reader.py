import os
import struct
import sys
from typing import Dict, List

import pandas as pd


def main(path: str):
    f = open(path, "rb")
    endian = "<"

    magic = f.read(4)
    if magic == b"EL-L":
        endian = ">"
    elif magic != b"L-LE":
        raise Exception("Invalid .ellog file.")
    
    data = f.read(8)
    ver, num_cha, num_cha = struct.unpack(f"{endian}IHH", data)
    if ver != 0x00000204:
        raise Exception("Unknown ILLOG version.")
    
    log: Dict[str, List[str]] = {}
    while num_cha > 0:
        len_cha = ord(f.read(1))
        data = f.read(len_cha)[:-1]
        log[data.decode()] = []
        num_cha -= 1

    len_unk = ord(f.read(1))
    f.read(len_unk)

    len_frame = len(log) * 4
    frame_fmt = endian
    for cha in log:
        if cha.startswith("TimeHigh") or cha.startswith("TimeLow"):
            frame_fmt += "I"
        else:
            frame_fmt += "f"

    while True:
        data = f.read(len_frame)
        if not data:
            break

        if len(data) < len_frame:
            raise Exception("File not fully read.")
        
        frame = struct.unpack(frame_fmt, data)
        for samples, sample in zip(log.values(), frame):
            samples.append(sample)

    f.close()
    output = path.replace(".ellog", ".csv")
    df = pd.DataFrame.from_dict(log)
    df.to_csv(output, index=False)
    print(f"Exported to {output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Must specify path to .ellogs.")
    
    if not os.path.isdir(sys.argv[1]):
        raise Exception(f"Directory {sys.argv[1]} does not exist.")
    
    for file in os.listdir(sys.argv[1]):
        full_path = os.path.join(sys.argv[1], file)
        if ".ellog" in full_path:
            print(f"Processing {full_path}")
            main(full_path)
