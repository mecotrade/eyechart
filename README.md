# EyeChart

## Description
The project contains simple renderer for visual acuity test charts. The output is either 
a single image file, or three printable at A4 paper images, which can be printed on standard 
office device and stitched together.

The following chart types are implemented:
* [Golovin-Sivtsev Table](https://en.wikipedia.org/wiki/Golovin%E2%80%93Sivtsev_table) with straight or curved letter K,
* The [Landolt C](https://en.wikipedia.org/wiki/Landolt_C), also known as a _Landolt ring_, _Landolt broken ring_, or _Japanese vision test_,
* [E chart](https://en.wikipedia.org/wiki/E_chart), also known as a _tumbling E chart_.

While passing frequently eye acuity test, any eye chart could be memorized, which makes
the test inefficient. To address this issue, for each chart type it is possible to produces 
both the standard symbol ordering and a shuffled version of the table. 

Different kinds of shuffling are possible:
* `shifted` the symbols order is the same, the leading symbol is shifted by a random number,
* `global_shuffle` symbols are globally shuffled,
* `line_shuffle` symbols are shuffled line-wise,
* `shifted_line_shuffle` the leading symbols is shifted by a random number, then symbols are shuffled line-wise,
* `random` random sample with replacement from standard list of symbols
* `smart_random` random sample with replacement and an attempt to avoid appearance of two or more same symbols in a row.

## Usage

To produce eye chart run the following command:
```bash
python eyechart.py -t <type> -g <shuffle>
```

The complete option description can be obtained as follows:
```bash
python eyechart.py -h
```