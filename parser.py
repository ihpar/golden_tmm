from collections import Counter
from fractions import Fraction


class SymbTextParser:
    def __init__(self):
        self.__note_line_codes = ["1", "4", "7",
                                  "9", "10", "11", "12",
                                  "23", "24", "28", "44"]

        self.__pitches = ["G", "A", "B", "C", "D", "E", "F"]
        self.__kommas = [9, 9, 4, 9, 9, 4, 9]

    def convert_to_sharp(self, note):
        """
        Converts notes with accidental symbols to all sharp rep.'s

        G --> G, 
        Bb9 --> A, 
        Eb4 --> D#5, 
        Bb1 --> A#8, 
        Bb13 --> G#5, 
        Gb5 --> F#4, 
        F#4 --> F#4, 
        E#4 --> F, 
        E#5 --> F#1, 
        E#13 --> G
        """

        if len(note) == 1:
            return note

        accidental = note[1]
        if accidental not in ["#", "b"]:
            raise ValueError("Accidental symbol unrecognised!")

        root = note[0]
        idx = self.__pitches.index(root)
        komma = int(note[2:])
        next_root, result = None, None
        remaining_komma = komma

        if accidental == "b":
            while remaining_komma > 0:
                idx = (idx - 1) % 7
                next_root = self.__pitches[idx]
                remaining_komma -= self.__kommas[idx]

            result = next_root
            if remaining_komma < 0:
                result += "#" + str(-1 * remaining_komma)

        elif accidental == "#":
            while remaining_komma > 0:
                remaining_komma -= self.__kommas[idx]
                idx = (idx + 1) % 7
                next_root = self.__pitches[idx]

            if remaining_komma < 0:
                idx = (idx - 1) % 7
                next_root = self.__pitches[idx]
                remaining_komma += self.__kommas[idx]

            result = next_root
            if remaining_komma != 0:
                result += "#" + str(remaining_komma)

        return result

    def get_pitch_classes(self, file_list, makam=None):
        all_pitches = []
        counts = Counter()

        for file_path in file_list:
            if makam and makam + "--" not in file_path:
                continue

            with open(file_path, "r") as in_file:
                lines = in_file.readlines()
                pitches = []
                for line in lines:
                    tokens = line.split("\t")
                    if tokens[1] in self.__note_line_codes:
                        note = tokens[3]
                        if note == "Es" or (not note[1].isdigit()):
                            continue

                        pitch_class = self.convert_to_sharp(note[0] + note[2:])
                        pitches.append(pitch_class)

                all_pitches.append(pitches)
                counts.update(pitches)

        return all_pitches, counts

    def get_pitch_classes_with_durations(self, file_list, as_pitch_classes=True):
        all_pitches = []
        all_durations = []
        for file_path in file_list:
            with open(file_path, "r") as in_file:
                lines = in_file.readlines()
            pitches = []
            durations = []
            for line in lines:
                tokens = line.split("\t")
                if tokens[1] not in self.__note_line_codes:
                    continue

                note = tokens[3]
                if note == "Es" or (not note[1].isdigit()):
                    pitch_class = "Es"
                    pitches.append(pitch_class)
                else:
                    pitch_class = self.convert_to_sharp(note[0] + note[2:])
                    if as_pitch_classes:
                        pitches.append(pitch_class)
                    else:
                        pitch_w_oct = pitch_class[0] + \
                            note[1] + pitch_class[1:]
                        pitches.append(pitch_w_oct)

                numerator = int(tokens[6])
                denominator = int(tokens[7])
                durations.append(Fraction(numerator, denominator))

            if len(pitches) != len(durations):
                raise Exception("Num pitches does not match len durations!")

            all_pitches.append(pitches)
            all_durations.append(durations)

        return all_pitches, all_durations


if __name__ == "__main__":
    parser = SymbTextParser()
    f = "data/txt/nihavent--sarki--nimsofyan--gozleri_aska--gundogdu_duran.txt"
    pitches, durations = parser.get_pitch_classes_with_durations([f],
                                                                 as_pitch_classes=False)
    print(pitches)
    print(durations)
