import argparse

from charts import GolovinSivtsev, LandoltC, EChart

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', default='golovin_sivtsev',
                        choices=('golovin_sivtsev', 'golovin_sivtsev_k_alt', 'landolt_c', 'e_chart'),
                        help='Eyechart type: "golovin_sivtsev" for Golovin-Sivtsev table,  "golovin_sivtsev_k_alt" '
                             'for Golovin-Sivtsev table with altered K letter, "landolt_c" for'
                             'Landolt C table, or "e_chart" for E-chart')
    parser.add_argument('-g', '--generator', default='smart_random',
                        choices=('random', 'smart_random', 'standard', 'shifted', 'global_shuffle', 'line_shuffle',
                                 'shifted_line_shuffle'),
                        help='Symbol generator type: "random" for purely random symbol appearance, "smart_random" for '
                             'random appearance where some efforts are made to avoid symbol repetition, "standard" '
                             'for standard symbol appearance, "shifted" for symbol appearance shifted with respect '
                             'to the standard once (Caesar cypher), "global_shuffle" for standard symbols globally '
                             'shuffled, "line_shuffle" for standard symbols shuffled line-wise, and '
                             '"shifted_line_shuffle" for combination of "line_shuffled: and "shifted"')
    parser.add_argument('-s', '--single', action='store_true', help='Single file, or 3 files to be printed on A4')
    parser.add_argument('-dpi', '--dots-per-inch', default=600, help='The output files resolution')
    parser.add_argument('-f', '--filename', default='table.png',
                        help='Output filename. For 3 files option index 1, 2, 3 is inserted before file extension.'
                             'Image compression is defined by extension, which is mandatory')

    args = parser.parse_args()

    if args.type == 'golovin_sivtsev':
        table = GolovinSivtsev()
    elif args.type == 'golovin_sivtsev_k_alt':
        table = GolovinSivtsev(k_alt=True)
    elif args.type == 'landolt_c':
        table = LandoltC()
    elif args.type == 'e_chart':
        table = EChart()
    else:
        raise NotImplementedError(args.type)

    table.save(args.generator, args.dots_per_inch, args.filename, args.single)
