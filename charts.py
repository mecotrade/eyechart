import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from abc import abstractmethod

from generator import RandomGenerator, SequenceGenerator


class EyeChart:
    
    A4_WIDTH_MM = 297
    A4_HEIGHT_MM = 209
    MM_PER_INCH = 25.4
    TABLE_WIDTH = 173
    V_OFFSET_MM_RIGHT = 40
    D_OFFSET_MM_LEFT = 30
    
    @abstractmethod
    def symbol_generator(self, generator_name):
        pass
    
    @abstractmethod
    def draw_symbol(self, draw, x, y, size, symbol):
        pass
    
    @staticmethod
    def x_positions(n, width, height, v):
        
        size = 7 / v
        space = (EyeChart.TABLE_WIDTH - n*size) / (n - 1)
        return [((EyeChart.A4_WIDTH_MM - EyeChart.TABLE_WIDTH)/2 +
                 (size + space)*k) / EyeChart.A4_WIDTH_MM * width
                for k in range(n)], size / EyeChart.A4_HEIGHT_MM * height
    
    def draw_sheet(self, width, height, offsets, ns, vs, generator):
    
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        fontsize = int(4.2 / EyeChart.A4_HEIGHT_MM * height)

        # https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pil-imagefont
        font = ImageFont.truetype(os.path.join('fonts', 'arial.ttf'), fontsize)
        ascent, descent = font.getmetrics()

        y = 0
        for offset, n, v in zip(offsets, ns, vs):    
            y += offset / EyeChart.A4_HEIGHT_MM * height
            xs, size = EyeChart.x_positions(n, width, height, v)
            symbols = generator.next_symbols(n)
            for x, symbol in zip(xs, symbols):
                self.draw_symbol(draw, x, y, size, symbol)

            if symbols:
                d_text = ('D = %.1f' % (5.0 / v)).replace('.', ',')
                v_text = ('V = %.1f' % v).replace('.', ',')
                _, (_, d_offset_y) = font.font.getsize(d_text)
                _, (_, v_offset_y) = font.font.getsize(v_text)
                draw.text((EyeChart.D_OFFSET_MM_LEFT / EyeChart.A4_WIDTH_MM * width,
                           y + size / 2 - (ascent - d_offset_y) / 2), d_text, (0, 0, 0), font=font)
                draw.text(((EyeChart.A4_WIDTH_MM - EyeChart.V_OFFSET_MM_RIGHT) / EyeChart.A4_WIDTH_MM * width,
                           y + size / 2 - (ascent - v_offset_y) / 2), v_text, (0, 0, 0), font=font)

            y += size

        return image
    
    def draw_sheet_1(self, width, height, generator):
        return self.draw_sheet(width, height, [20, 23, 23], 
                               [2, 3, 4], [0.1, 0.2, 0.3], generator)

    def draw_sheet_2(self, width, height, generator):
        return self.draw_sheet(width, height, [14, 23, 23, 23, 23, 23], 
                               [5, 5, 6, 6, 7, 7], [0.4, 0.5, 0.6, 0.7, 0.8, 0.9], generator)

    def draw_sheet_3(self, width, height, generator):
        image = self.draw_sheet(width, height, [13, 23, 23, 36, 23, 23], 
                                [8, 8, 8, 10, 10, 10], [1.0, 1.5, 2.0, 3.0, 4.0, 5.0], generator)
    
        draw = ImageDraw.Draw(image)
        draw.rectangle(((1./EyeChart.A4_WIDTH_MM * width, 28./EyeChart.A4_HEIGHT_MM * height),
                        ((EyeChart.A4_WIDTH_MM - 6.)/EyeChart.A4_WIDTH_MM*width, 28.7/EyeChart.A4_HEIGHT_MM * height)),
                       fill='black')
        draw.line(((1./EyeChart.A4_WIDTH_MM * width, 98./EyeChart.A4_HEIGHT_MM * height),
                   ((EyeChart.A4_WIDTH_MM - 6.)/EyeChart.A4_WIDTH_MM * width, 98./EyeChart.A4_HEIGHT_MM * height)),
                  fill='black')

        return image
    
    @staticmethod
    def save_image(image, filename):
        head, tail = os.path.split(filename)
        if head:
            if not os.path.exists(head):
                os.makedirs(head)
        image.save(filename)
    
    def save(self, generator_name, dpi=600, filename='sheet.png', single=False):

        generator = self.symbol_generator(generator_name)

        width = int(EyeChart.A4_WIDTH_MM * dpi / EyeChart.MM_PER_INCH)
        height = int(EyeChart.A4_HEIGHT_MM * dpi / EyeChart.MM_PER_INCH)
        
        if single:
            result = Image.new('RGB', (width, 3*height))
            for i, method in enumerate([self.draw_sheet_1, self.draw_sheet_2, self.draw_sheet_3]):
                image = method(width, height, generator)
                result.paste(im=image, box=(0, i*height))
            EyeChart.save_image(result, filename)
            print('File %s saved' % filename)
        else:        
            file, ext = os.path.splitext(filename)
            assert ext, 'Filename should contain an extention'
            
            for i, method in enumerate([self.draw_sheet_1, self.draw_sheet_2, self.draw_sheet_3]):
                image = method(width, height, generator)
                image_name = '%s%d%s' % (file, i + 1, ext)
                EyeChart.save_image(image, image_name)
                print('File %s saved' % image_name)


class LettersChart(EyeChart):
    
    # Ш=0, Б=1, М=2, Н=3, К=4, Ы=5, И=6
    STANDARD_SYMBOLS = [0, 1,                            # Ш Б
                        2, 3, 4,                         # М Н К
                        5, 2, 1, 0,                      # Ы М Б Ш
                       
                        1, 5, 3, 4, 2,                   # Б Ы Н К М
                        6, 3, 0, 2, 4,                   # И Н Ш М К
                        3, 0, 5, 6, 4, 1,                # Н Ш Ы И К Б
                        0, 6, 3, 1, 4, 5,                # Ш И Н Б К Ы
                        4, 3, 0, 2, 5, 1, 6,             # К Н Ш М Ы Б И
                        1, 4, 0, 2, 6, 5, 3,             # Б К Ш М И Ы Н
                       
                        3, 4, 6, 1, 2, 0, 5, 1,          # Н К И Б М Ш Ы Б
                        0, 6, 3, 4, 2, 6, 5, 1,          # Ш И Н К М И Ы Б
                        6, 2, 0, 5, 3, 1, 2, 4,          # И М Ш Ы Н Б М К
                        0, 1, 4, 5, 3, 1, 2, 0, 6, 2,    # Ш Б К Ы Н Б М Ш И М
                        2, 5, 0, 1, 6, 2, 0, 3, 4, 1,    # М Ы Ш Б И М Ш Н К Б
                        6, 1, 5, 3, 2, 1, 6, 3, 0, 4]    # И Б Ы Н М Б И Н Ш К
    
    def __init__(self, k_alt=False):
        
        self.symbol_func = [LettersChart.draw_sh,
                            LettersChart.draw_b,
                            LettersChart.draw_m,
                            LettersChart.draw_n,
                            LettersChart.draw_k_alt if k_alt else LettersChart.draw_k,
                            LettersChart.draw_y,
                            LettersChart.draw_i]

    @staticmethod
    def draw_sh(draw, x, y, size):
        width = size / 5
        draw.rectangle(((x, y + size), (x + size, y + size - width)), fill='black')
        draw.rectangle(((x, y + size - width), (x + width, y)), fill='black')
        draw.rectangle(((x + 2*width, y + size - width), (x + 3*width, y)), fill='black')
        draw.rectangle(((x + 4*width, y + size - width), (x + size, y)), fill='black')
    
    @staticmethod
    def draw_b(draw, x, y, size):
        width = size / 5
        draw.rectangle(((x, y + size), (x + width, y)), fill='black')
        draw.rectangle(((x, y + width), (x + size, y)), fill='black')
        draw.ellipse((x + 2*width, y + 2*width, x + size, y + size), fill='black', outline='black')
        draw.ellipse((x + 3*width, y + 3*width, x + 4*width, y + 4*width), fill = 'white', outline='black')
        draw.rectangle(((x + width, y + 4*width), (x + 3.5*width, y + 3*width)), fill='white', outline='white')
        draw.rectangle(((x + width, y + 3*width), (x + 3.5*width, y + 2*width)), fill='black')
        draw.rectangle(((x + width, y + 5*width), (x + 3.5*width, y + 4*width)), fill='black')
        
    @staticmethod
    def draw_m(draw, x, y, size):
        width = size / 5
        draw.rectangle(((x, y), (x + width, y + size)), fill='black')
        draw.rectangle(((x + 4*width, y), (x + size, y + size)), fill='black')
        draw.polygon(((x, y), (x + width, y), (x + 3*width, y + size), (x + 2*width, y + size)), fill='black')
        draw.polygon(((x + 4*width, y), (x + size, y), (x + 3*width, y + size), (x + 2*width, y + size)), fill='black')
        
    @staticmethod
    def draw_n(draw, x, y, size):
        width = size / 5
        draw.rectangle(((x, y), (x + width, y + size)), fill='black')
        draw.rectangle(((x + 4*width, y), (x + size, y + size)), fill='black')
        draw.rectangle(((x + width, y + 2*width), (x + 4*width, y + 3*width)), fill='black')
        
    @staticmethod
    def draw_k(draw, x, y, size):
        width = size / 5
        draw.chord((x - width, y - 3*width, x + size, y + 3*width), 0, 180, fill='black')
        draw.chord((x, y - 2*width, x + 4*width, y + 2*width), 0, 180, fill='white', outline='white')
        draw.line(((x - width, y - 1), (x + size, y - 1)), fill='white')
        draw.rectangle(((x + width, y), (x + 2*width, y + 2*width)), fill='white', outline='white')
        draw.chord((x - width, y + 2*width, x + size, y + 8*width), 180, 360, fill='black')
        draw.chord((x, y + 3*width, x + 4*width, y + 7*width), 180, 360, fill='white', outline='white')
        draw.line(((x - width, y + size), (x + size, y + size)), fill='white')
        draw.rectangle(((x + width, y + 3*width), (x + 2*width, y + size)), fill='white', outline='white')
        draw.rectangle(((x - width, y), (x, y + size)), fill='white', outline='white')
        draw.rectangle(((x, y), (x + width, y + size)), fill='black')
        draw.rectangle(((x + width, y + 2*width), (x + 3*width, y + 3*width)), fill='black')
        
    @staticmethod
    def draw_k_alt(draw, x, y, size):
        width = size / 5
        draw.rectangle(((x, y), (x + width, y + size)), fill='black')
        draw.rectangle(((x + width, y + 2*width), (x + 3*width, y + 3*width)), fill='black')
        draw.chord((x + width, y - 3*width, x + size, y + 3*width), 0, 180, fill='black')
        draw.chord((x + 2*width, y - 2*width, x + 4*width, y + 2*width), 0, 180, fill='white', outline='white')
        draw.rectangle(((x + width, y), (x + 3*width, y + 2*width)), fill='white', outline='white')
        draw.line(((x - width, y - 1), (x + size, y - 1)), fill='white')
        draw.chord((x + width, y + 2*width, x + size, y + 8*width), 180, 360, fill='black')
        draw.chord((x + 2*width, y + 3*width, x + 4*width, y + 7*width), 180, 360, fill='white', outline='white')
        draw.rectangle(((x + width, y + 3*width), (x + 3*width, y + size)), fill='white', outline='white')
        draw.line(((x - width, y + size), (x + size, y + size)), fill='white')

    @staticmethod
    def draw_y(draw, x, y, size):
        width = size / 5
        draw.rectangle(((x, y), (x + width, y + size)), fill='black')
        draw.rectangle(((x + 4*width, y), (x + size, y + size)), fill='black')
        draw.ellipse((x + 0.5 * width, y + 2*width, x + 3.5 * width, y + size), fill='black', outline='black')
        draw.ellipse((x + 1.5 * width, y + 3*width, x + 2.5 * width, y + 4*width), fill='white', outline='black')
        draw.rectangle(((x + width, y + 2 * width), (x + 2 * width, y + 3 * width)), fill='black')
        draw.rectangle(((x + width, y + 3 * width), (x + 2 * width, y + 4 * width)), fill='white', outline='white')
        draw.rectangle(((x + width, y + 4 * width), (x + 2 * width, y + 5 * width)), fill='black')
        
    @staticmethod
    def draw_i(draw, x, y, size):
        width = size / 5
        draw.rectangle(((x, y), (x + width, y + size)), fill='black')
        draw.rectangle(((x + 4*width, y), (x + size, y + size)), fill='black')
        draw.polygon(((x + width, y + size), (x + 4*width, y + 1.5*width), 
                      (x + 4*width, y), (x + width, y + 3.5*width)), fill='black')
        
    def draw_symbol(self, draw, x, y, size, symbol):
        self.symbol_func[symbol](draw, x, y, size)
        
    def symbol_generator(self, generator_name):
    
        if 'standard' == generator_name:
            return SequenceGenerator(sequence=LettersChart.STANDARD_SYMBOLS)
        elif 'shifted' == generator_name:
            global_shift = np.random.randint(0, len(LettersChart.STANDARD_SYMBOLS), 1)[0]
            return SequenceGenerator(sequence=LettersChart.STANDARD_SYMBOLS, global_shift=global_shift)
        elif 'global_shuffle' == generator_name:
            return SequenceGenerator(sequence=LettersChart.STANDARD_SYMBOLS, shuffle='global')
        elif 'line_shuffle' == generator_name:
            return SequenceGenerator(sequence=LettersChart.STANDARD_SYMBOLS, shuffle='line')
        elif 'shifted_line_shuffle' == generator_name:
            global_shift = np.random.randint(0, len(LettersChart.STANDARD_SYMBOLS), 1)[0]
            return SequenceGenerator(sequence=LettersChart.STANDARD_SYMBOLS, global_shift=global_shift, shuffle='line')
        elif 'random' == generator_name:
            return RandomGenerator(n_symbols=len(self.symbol_func))
        elif 'smart_random' == generator_name:
            return RandomGenerator(n_symbols=len(self.symbol_func), smart=True)
        else:
            raise NotImplementedError(generator_name)


class CirclesChart(EyeChart):

    # V=0, <=1, ^=2, >=3
    STANDARD_SYMBOLS = [3, 1,                       # > <
                        1, 2, 3,                    # < ^ >
                        2, 3, 0, 1,                 # ^ > V <

                        3, 0, 2, 1, 0,              # > V ^ < V
                        1, 3, 2, 0, 3,              # < > ^ V >
                        2, 1, 0, 3, 1, 2,           # ^ < V > < ^
                        3, 2, 3, 1, 2, 3,           # > ^ > < ^ >
                        1, 3, 0, 2, 1, 0, 1,        # < > V ^ < V <
                        0, 2, 3, 1, 0, 3, 2,        # V ^ > < V > ^

                        1, 3, 0, 3, 2, 1, 0, 3,     # < > V > ^ < V >
                        3, 0, 2, 1, 2, 0, 3, 2,     # > V ^ < ^ V > ^
                        0, 3, 0, 2, 1, 3, 2, 1]     # V > V ^ < > ^ <

    def __init__(self):
        
        self.symbol_func = [CirclesChart.draw_circle_up,
                            CirclesChart.draw_circle_right,
                            CirclesChart.draw_circle_down,
                            CirclesChart.draw_circle_left]
    
    @staticmethod
    def draw_circle_up(draw, x, y, size):
        width = size / 5
        draw.ellipse((x, y, x + size, y + size), fill='black', outline='black')
        draw.ellipse((x + width, y + width, x + 4*width, y + 4*width), fill='white', outline='white')
        draw.rectangle(((x + 2*width, y), (x + 3*width, y + 2*width)), fill='white', outline='white')
        
    @staticmethod
    def draw_circle_right(draw, x, y, size):
        width = size / 5
        draw.ellipse((x, y, x + size, y + size), fill='black', outline='black')
        draw.ellipse((x + width, y + width, x + 4*width, y + 4*width), fill='white', outline='white')
        draw.rectangle(((x + 3*width, y + 2*width), (x + size, y + 3*width)), fill='white', outline='white')
        
    @staticmethod
    def draw_circle_down(draw, x, y, size):
        width = size / 5
        draw.ellipse((x, y, x + size, y + size), fill='black', outline='black')
        draw.ellipse((x + width, y + width, x + 4*width, y + 4*width), fill='white', outline='white')
        draw.rectangle(((x + 2*width, y + 3*width), (x + 3*width, y + size)), fill='white', outline='white')
                            
    @staticmethod
    def draw_circle_left(draw, x, y, size):
        width = size / 5
        draw.ellipse((x, y, x + size, y + size), fill='black', outline='black')
        draw.ellipse((x + width, y + width, x + 4*width, y + 4*width), fill='white', outline='white')
        draw.rectangle(((x, y + 2*width), (x + 2*width, y + 3*width)), fill='white', outline='white')
        
    def draw_symbol(self, draw, x, y, size, symbol):
        self.symbol_func[symbol](draw, x, y, size)
        
    def symbol_generator(self, generator_name):

        if 'standard' == generator_name:
            return SequenceGenerator(sequence=CirclesChart.STANDARD_SYMBOLS)
        elif 'shifted' == generator_name:
            global_shift = np.random.randint(0, len(CirclesChart.STANDARD_SYMBOLS), 1)[0]
            return SequenceGenerator(sequence=CirclesChart.STANDARD_SYMBOLS, global_shift=global_shift)
        elif 'global_shuffle' == generator_name:
            return SequenceGenerator(sequence=CirclesChart.STANDARD_SYMBOLS, shuffle='global')
        elif 'line_shuffle' == generator_name:
            return SequenceGenerator(sequence=CirclesChart.STANDARD_SYMBOLS, shuffle='line')
        elif 'shifted_line_shuffle' == generator_name:
            global_shift = np.random.randint(0, len(CirclesChart.STANDARD_SYMBOLS), 1)[0]
            return SequenceGenerator(sequence=CirclesChart.STANDARD_SYMBOLS, global_shift=global_shift, shuffle='line')
        elif 'random' == generator_name:
            return RandomGenerator(n_symbols=len(self.symbol_func))
        elif 'smart_random' == generator_name:
            return RandomGenerator(n_symbols=len(self.symbol_func), smart=True)
        else:
            raise NotImplementedError(generator_name)