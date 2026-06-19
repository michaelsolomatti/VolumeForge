// VolumeCalculator.cs - Калькулятор объёма тел на C# (CLI)
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace VolumeCalculator
{
    class Shape
    {
        public string Name { get; set; }
        public Func<double[], double> Func { get; set; }
        public string[] Params { get; set; }
    }

    class HistoryEntry
    {
        public string Date { get; set; }
        public string Shape { get; set; }
        public string Params { get; set; }
        public string Result { get; set; }
        public string Units { get; set; }
    }

    class Program
    {
        private static readonly double PI = Math.PI;
        private static readonly string HISTORY_FILE = "volume_history.json";
        private static readonly Dictionary<string, Shape> shapes = new Dictionary<string, Shape>();

        static Program()
        {
            shapes["1"] = new Shape { Name = "Куб", Func = p => Math.Pow(p[0], 3), Params = new[] { "сторону" } };
            shapes["2"] = new Shape { Name = "Шар", Func = p => 4.0/3.0 * PI * Math.Pow(p[0], 3), Params = new[] { "радиус" } };
            shapes["3"] = new Shape { Name = "Цилиндр", Func = p => PI * Math.Pow(p[0], 2) * p[1], Params = new[] { "радиус", "высоту" } };
            shapes["4"] = new Shape { Name = "Конус", Func = p => 1.0/3.0 * PI * Math.Pow(p[0], 2) * p[1], Params = new[] { "радиус", "высоту" } };
            shapes["5"] = new Shape { Name = "Параллелепипед", Func = p => p[0] * p[1] * p[2], Params = new[] { "длину", "ширину", "высоту" } };
            shapes["6"] = new Shape { Name = "Пирамида", Func = p => 1.0/3.0 * p[0] * p[1], Params = new[] { "площадь основания", "высоту" } };
            shapes["7"] = new Shape { Name = "Призма", Func = p => p[0] * p[1], Params = new[] { "площадь основания", "высоту" } };
            shapes["8"] = new Shape { Name = "Тор", Func = p => 2.0 * Math.Pow(PI, 2) * p[0] * Math.Pow(p[1], 2), Params = new[] { "большой радиус", "малый радиус" } };
            shapes["9"] = new Shape { Name = "Эллипсоид", Func = p => 4.0/3.0 * PI * p[0] * p[1] * p[2], Params = new[] { "полуось a", "полуось b", "полуось c" } };
            shapes["10"] = new Shape { Name = "Усечённый конус", Func = p => 1.0/3.0 * PI * p[2] * (Math.Pow(p[0], 2) + p[0]*p[1] + Math.Pow(p[1], 2)), Params = new[] { "радиус 1", "радиус 2", "высоту" } };
        }

        static void SaveHistory(HistoryEntry entry)
        {
            List<HistoryEntry> history = LoadHistory();
            history.Add(entry);
            string json = JsonSerializer.Serialize(history, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(HISTORY_FILE, json);
        }

        static List<HistoryEntry> LoadHistory()
        {
            if (File.Exists(HISTORY_FILE))
            {
                try
                {
                    string json = File.ReadAllText(HISTORY_FILE);
                    return JsonSerializer.Deserialize<List<HistoryEntry>>(json) ?? new List<HistoryEntry>();
                }
                catch { }
            }
            return new List<HistoryEntry>();
        }

        static void ExportCSV(string filename)
        {
            var history = LoadHistory();
            if (!history.Any())
            {
                Console.WriteLine("История пуста.");
                return;
            }
            using (var sw = new StreamWriter(filename))
            {
                sw.WriteLine("Дата,Фигура,Параметры,Объём,Единицы");
                foreach (var e in history)
                {
                    string units = string.IsNullOrEmpty(e.Units) ? "куб. ед." : e.Units;
                    sw.WriteLine($"{e.Date.Substring(0,19)},{e.Shape},\"{e.Params}\",{e.Result},{units}");
                }
            }
            Console.WriteLine($"Экспортировано в {filename}");
        }

        static double GetDouble(string prompt)
        {
            while (true)
            {
                Console.Write(prompt);
                string input = Console.ReadLine();
                if (double.TryParse(input, out double val) && val > 0)
                    return val;
                Console.WriteLine("Введите положительное число.");
            }
        }

        static void Main()
        {
            Console.WriteLine("📦 КАЛЬКУЛЯТОР ОБЪЁМА ТЕЛ");
            var history = LoadHistory();
            string units = "куб. ед.";

            while (true)
            {
                Console.WriteLine("\nВыберите фигуру:");
                foreach (var kv in shapes)
                    Console.WriteLine($"{kv.Key}. {kv.Value.Name}");
                Console.WriteLine("h. Показать историю");
                Console.WriteLine("e. Экспорт CSV");
                Console.WriteLine("u. Сменить единицы");
                Console.WriteLine("0. Выход");

                string choice = Console.ReadLine();

                if (choice == "0") break;
                else if (choice?.ToLower() == "h")
                {
                    if (!history.Any())
                    {
                        Console.WriteLine("История пуста.");
                    }
                    else
                    {
                        Console.WriteLine("\n=== ИСТОРИЯ ===");
                        foreach (var e in history.Skip(Math.Max(0, history.Count - 10)))
                            Console.WriteLine($"{e.Date.Substring(0, 19)} | {e.Shape} | {e.Result}");
                    }
                    continue;
                }
                else if (choice?.ToLower() == "e")
                {
                    Console.Write("Имя CSV файла (по умолчанию volume_history.csv): ");
                    string filename = Console.ReadLine();
                    if (string.IsNullOrEmpty(filename)) filename = "volume_history.csv";
                    ExportCSV(filename);
                    continue;
                }
                else if (choice?.ToLower() == "u")
                {
                    Console.WriteLine("Доступные единицы: куб. ед., см³, м³, дм³, л, in³");
                    Console.Write("Выберите единицы: ");
                    string input = Console.ReadLine();
                    if (!string.IsNullOrEmpty(input)) units = input;
                    continue;
                }
                else if (shapes.ContainsKey(choice))
                {
                    var shape = shapes[choice];
                    Console.WriteLine($"\nФигура: {shape.Name}");
                    var paramsList = new List<double>();
                    foreach (var pname in shape.Params)
                        paramsList.Add(GetDouble($"Введите {pname}: "));
                    double result = shape.Func(paramsList.ToArray());
                    string resultStr = $"{result:F4} {units}";
                    Console.WriteLine($"\nОбъём {shape.Name.ToLower()}: {resultStr}");

                    Console.Write("Сохранить результат? (y/n): ");
                    if (Console.ReadLine()?.ToLower() == "y")
                    {
                        var entry = new HistoryEntry
                        {
                            Date = DateTime.Now.ToString("o"),
                            Shape = shape.Name,
                            Params = string.Join(", ", paramsList),
                            Result = resultStr,
                            Units = units
                        };
                        SaveHistory(entry);
                        history.Add(entry);
                        Console.WriteLine("✅ Сохранено!");
                    }
                }
                else
                {
                    Console.WriteLine("Неверный выбор.");
                }
            }
        }
    }
}
