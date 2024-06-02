// Сборка русских символов
// Оригинал: https://github.com/ssilver2007/LCD_1602_RUS/blob/master/LCD_1602_RUS.cpp

const chars = [
  { c: "Б", data: [0b11111, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b11110, 0b00000] },
  { c: "Г", data: [0b11111, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b00000] },
  { c: "Д", data: [0b00110, 0b01010, 0b01010, 0b01010, 0b01010, 0b01010, 0b11111, 0b10001] },
  { c: "Ж", data: [0b10101, 0b10101, 0b10101, 0b01110, 0b10101, 0b10101, 0b10101, 0b00000] },
  { c: "З", data: [0b01110, 0b10001, 0b00001, 0b00110, 0b00001, 0b10001, 0b01110, 0b00000] },
  { c: "И", data: [0b10001, 0b10001, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b00000] },
  { c: "Й", data: [0b10101, 0b10001, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b00000] },
  { c: "Л", data: [0b00111, 0b01001, 0b01001, 0b01001, 0b01001, 0b01001, 0b10001, 0b00000] },
  { c: "П", data: [0b11111, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b00000] },
  { c: "У", data: [0b10001, 0b10001, 0b10001, 0b01111, 0b00001, 0b10001, 0b01110, 0b00000] },
  { c: "Ф", data: [0b00100, 0b01110, 0b10101, 0b10101, 0b10101, 0b01110, 0b00100, 0b00000] },
  { c: "Ц", data: [0b10010, 0b10010, 0b10010, 0b10010, 0b10010, 0b10010, 0b11111, 0b00001] },
  { c: "Ч", data: [0b10001, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b00001, 0b00000] },
  { c: "Ш", data: [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b11111, 0b00000] },
  { c: "Щ", data: [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b11111, 0b00001] },
  { c: "Ъ", data: [0b11000, 0b01000, 0b01000, 0b01110, 0b01001, 0b01001, 0b01110, 0b00000] },
  { c: "Ы", data: [0b10001, 0b10001, 0b10001, 0b11101, 0b10011, 0b10011, 0b11101, 0b00000] },
  { c: "Ь", data: [0b10000, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b11110, 0b00000] },
  { c: "Э", data: [0b01110, 0b10001, 0b00001, 0b00111, 0b00001, 0b10001, 0b01110, 0b00000] },
  { c: "Ю", data: [0b10010, 0b10101, 0b10101, 0b11101, 0b10101, 0b10101, 0b10010, 0b00000] },
  { c: "Я", data: [0b01111, 0b10001, 0b10001, 0b01111, 0b00101, 0b01001, 0b10001, 0b00000] },

  { c: "б", data: [0b00011, 0b01100, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110, 0b00000] },
  { c: "в", data: [0b00000, 0b00000, 0b11110, 0b10001, 0b11110, 0b10001, 0b11110, 0b00000] },
  { c: "г", data: [0b00000, 0b00000, 0b11110, 0b10000, 0b10000, 0b10000, 0b10000, 0b00000] },
  { c: "д", data: [0b00000, 0b00000, 0b00110, 0b01010, 0b01010, 0b01010, 0b11111, 0b10001] },
  { c: "ё", data: [0b01010, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01111, 0b00000] },
  { c: "ж", data: [0b00000, 0b00000, 0b10101, 0b10101, 0b01110, 0b10101, 0b10101, 0b00000] },
  { c: "з", data: [0b00000, 0b00000, 0b01110, 0b10001, 0b00110, 0b10001, 0b01110, 0b00000] },
  { c: "и", data: [0b00000, 0b00000, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b00000] },
  { c: "й", data: [0b01010, 0b00100, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b00000] },
  { c: "к", data: [0b00000, 0b00000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b00000] },
  { c: "л", data: [0b00000, 0b00000, 0b00111, 0b01001, 0b01001, 0b01001, 0b10001, 0b00000] },
  { c: "м", data: [0b00000, 0b00000, 0b10001, 0b11011, 0b10101, 0b10001, 0b10001, 0b00000] },
  { c: "н", data: [0b00000, 0b00000, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b00000] },
  { c: "п", data: [0b00000, 0b00000, 0b11111, 0b10001, 0b10001, 0b10001, 0b10001, 0b00000] },
  { c: "т", data: [0b00000, 0b00000, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000] },
  { c: "ф", data: [0b00000, 0b00000, 0b00100, 0b01110, 0b10101, 0b01110, 0b00100, 0b00000] },
  { c: "ц", data: [0b00000, 0b00000, 0b10010, 0b10010, 0b10010, 0b10010, 0b11111, 0b00001] },
  { c: "ч", data: [0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b00000] },
  { c: "ш", data: [0b00000, 0b00000, 0b10101, 0b10101, 0b10101, 0b10101, 0b11111, 0b00000] },
  { c: "щ", data: [0b00000, 0b00000, 0b10101, 0b10101, 0b10101, 0b10101, 0b11111, 0b00001] },
  { c: "ъ", data: [0b00000, 0b00000, 0b11000, 0b01000, 0b01110, 0b01001, 0b01110, 0b00000] },
  { c: "ы", data: [0b00000, 0b00000, 0b10001, 0b10001, 0b11101, 0b10011, 0b11101, 0b00000] },
  { c: "ь", data: [0b00000, 0b00000, 0b10000, 0b10000, 0b11110, 0b10001, 0b11110, 0b00000] },
  { c: "э", data: [0b00000, 0b00000, 0b01110, 0b10001, 0b00111, 0b10001, 0b01110, 0b00000] },
  { c: "ю", data: [0b00000, 0b00000, 0b10010, 0b10101, 0b11101, 0b10101, 0b10010, 0b00000] },
  { c: "я", data: [0b00000, 0b00000, 0b01111, 0b10001, 0b01111, 0b00101, 0b01001, 0b00000] },
]

const list_5x8 = [];

for (const char of chars) {
  const bytes = [0, 0, 0, 0, 0];

  for (let c = 0; c < 5; c += 1) {
    for (let r = 0; r < 8; r += 1) {
      bytes[c] |= ((char.data[r] >> (4 - c)) & 0b1) << r;
    }
  }

  list_5x8.push({ c: char.c, code: char.c.charCodeAt(0), bytes })
}

// console.log(res);

const ranges = [];

list_5x8.sort((a, b) => a.code - b.code);

let range = { start: -1, end: -1, data: [] };

for (let i = 0; i < list_5x8.length; i += 1) {
  const char = list_5x8[i];

  if (range.end + 1 !== char.code) {
    ranges.push(range = { start: char.code, end: char.code, data: [] });
  }

  range.end = char.code;
  range.data.push(...char.bytes);
}

const python = [
  "width = 5",
  "height = 8",
  "font_cyrillic = [",
  "# start_code, end_code, data",
  ranges.map((range) => `[${[range.start, range.end, `bytearray([${range.data.map((b) => `0x${Number(b).toString(16)}`).join(",")}])`].join(", ")}]`).join(",\n"),
  "]"
].join("\n");

console.log(python);
