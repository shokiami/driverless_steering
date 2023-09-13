import os
import shutil
import struct
import pandas as pd

IN_DIR = 'drive_data'
OUT_DIR = 'drive_csvs'

shutil.rmtree(OUT_DIR)
os.makedirs(OUT_DIR)

for ellog in os.listdir(IN_DIR):
  if '.ellog' in ellog:
    print(f'processing {ellog}...')
    f = open(os.path.join(IN_DIR, ellog), 'rb')
    endian = '<'

    magic = f.read(4)
    if magic == b'EL-L':
      endian = '>'
    elif magic != b'L-LE':
      raise Exception('Invalid .ellog file.')
    
    data = f.read(8)
    ver, num_cha, num_cha = struct.unpack(f'{endian}IHH', data)
    if ver != 0x00000204:
      raise Exception('Unknown ILLOG version.')
    
    log = {}
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
      if cha.startswith('TimeHigh') or cha.startswith('TimeLow'):
        frame_fmt += 'I'
      else:
        frame_fmt += 'f'

    while True:
      data = f.read(len_frame)
      if not data:
        break

      if len(data) < len_frame:
        raise Exception('File not fully read.')
      
      frame = struct.unpack(frame_fmt, data)
      for samples, sample in zip(log.values(), frame):
        samples.append(sample)

    f.close()
    df = pd.DataFrame.from_dict(log)
    df.to_csv(os.path.join(OUT_DIR, ellog.replace('.ellog', '.csv')), index=False)
