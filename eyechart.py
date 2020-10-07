import argparse

from charts import LettersChart, CirclesChart

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', default='letters', choices=('letters', 'letters_k_alt', 'circles'),
                        help='Eyechart type: "letters" for Sivtsev-Golovin eyechart,  "letters_k_alt" '
                             'for Sivtsev-Golovin eyechart with altered K letter, or "circles" for'
                             'eyechart with Landolt C symbols')
    parser.add_argument('-g', '--generator', default='smart_random',
                        choices=('random', 'smart_random', 'standard', 'shifted', 'global_shuffle', 'line_shuffle',
                                 'shifted_line_shuffle', ''),
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

    if args.type == 'letters':
        table = LettersChart()
    elif args.type == 'letters_alt_k':
        table = LettersChart(k_alt=True)
    else:
        table = CirclesChart()

    table.save(args.generator, args.dots_per_inch, args.filename, args.single)
