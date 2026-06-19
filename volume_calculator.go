// volume_calculator.go - Калькулятор объёма тел на Go (CLI)
package main

import (
	"bufio"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"math"
	"os"
	"strconv"
	"strings"
	"time"
)

const PI = math.Pi
const HISTORY_FILE = "volume_history.json"

type Shape struct {
	Name   string
	Func   func([]float64) float64
	Params []string
}

type HistoryEntry struct {
	Date   string `json:"date"`
	Shape  string `json:"shape"`
	Params string `json:"params"`
	Result string `json:"result"`
	Units  string `json:"units"`
}

var shapes = map[string]Shape{
	"1":  {"Куб", func(p []float64) float64 { return math.Pow(p[0], 3) }, []string{"сторону"}},
	"2":  {"Шар", func(p []float64) float64 { return 4.0 / 3.0 * PI * math.Pow(p[0], 3) }, []string{"радиус"}},
	"3":  {"Цилиндр", func(p []float64) float64 { return PI * math.Pow(p[0], 2) * p[1] }, []string{"радиус", "высоту"}},
	"4":  {"Конус", func(p []float64) float64 { return 1.0 / 3.0 * PI * math.Pow(p[0], 2) * p[1] }, []string{"радиус", "высоту"}},
	"5":  {"Параллелепипед", func(p []float64) float64 { return p[0] * p[1] * p[2] }, []string{"длину", "ширину", "высоту"}},
	"6":  {"Пирамида", func(p []float64) float64 { return 1.0 / 3.0 * p[0] * p[1] }, []string{"площадь основания", "высоту"}},
	"7":  {"Призма", func(p []float64) float64 { return p[0] * p[1] }, []string{"площадь основания", "высоту"}},
	"8":  {"Тор", func(p []float64) float64 { return 2.0 * math.Pow(PI, 2) * p[0] * math.Pow(p[1], 2) }, []string{"большой радиус", "малый радиус"}},
	"9":  {"Эллипсоид", func(p []float64) float64 { return 4.0 / 3.0 * PI * p[0] * p[1] * p[2] }, []string{"полуось a", "полуось b", "полуось c"}},
	"10": {"Усечённый конус", func(p []float64) float64 { return 1.0 / 3.0 * PI * p[2] * (math.Pow(p[0], 2) + p[0]*p[1] + math.Pow(p[1], 2)) }, []string{"радиус 1", "радиус 2", "высоту"}},
}

func saveHistory(entry HistoryEntry) {
	var history []HistoryEntry
	file, err := os.ReadFile(HISTORY_FILE)
	if err == nil {
		json.Unmarshal(file, &history)
	}
	history = append(history, entry)
	data, _ := json.MarshalIndent(history, "", "  ")
	os.WriteFile(HISTORY_FILE, data, 0644)
}

func loadHistory() []HistoryEntry {
	var history []HistoryEntry
	file, err := os.ReadFile(HISTORY_FILE)
	if err != nil {
		return history
	}
	json.Unmarshal(file, &history)
	return history
}

func exportCSV(filename string) {
	history := loadHistory()
	if len(history) == 0 {
		fmt.Println("История пуста.")
		return
	}
	f, _ := os.Create(filename)
	defer f.Close()
	writer := csv.NewWriter(f)
	defer writer.Flush()
	writer.Write([]string{"Дата", "Фигура", "Параметры", "Объём", "Единицы"})
	for _, e := range history {
		units := e.Units
		if units == "" {
			units = "куб. ед."
		}
		writer.Write([]string{e.Date[:19], e.Shape, e.Params, e.Result, units})
	}
	fmt.Printf("Экспортировано в %s\n", filename)
}

func getFloat(prompt string, reader *bufio.Reader) float64 {
	for {
		fmt.Print(prompt)
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)
		val, err := strconv.ParseFloat(input, 64)
		if err == nil && val > 0 {
			return val
		}
		fmt.Println("Введите положительное число.")
	}
}

func main() {
	reader := bufio.NewReader(os.Stdin)
	fmt.Println("📦 КАЛЬКУЛЯТОР ОБЪЁМА ТЕЛ")
	history := loadHistory()
	units := "куб. ед."

	for {
		fmt.Println("\nВыберите фигуру:")
		for key, shape := range shapes {
			fmt.Printf("%s. %s\n", key, shape.Name)
		}
		fmt.Println("h. Показать историю")
		fmt.Println("e. Экспорт CSV")
		fmt.Println("u. Сменить единицы")
		fmt.Println("0. Выход")

		fmt.Print("Ваш выбор: ")
		choice, _ := reader.ReadString('\n')
		choice = strings.TrimSpace(choice)

		if choice == "0" {
			break
		} else if choice == "h" || choice == "H" {
			if len(history) == 0 {
				fmt.Println("История пуста.")
			} else {
				fmt.Println("\n=== ИСТОРИЯ ===")
				start := len(history) - 10
				if start < 0 {
					start = 0
				}
				for i := start; i < len(history); i++ {
					e := history[i]
					fmt.Printf("%s | %s | %s\n", e.Date[:19], e.Shape, e.Result)
				}
			}
			continue
		} else if choice == "e" || choice == "E" {
			fmt.Print("Имя CSV файла (по умолчанию volume_history.csv): ")
			filename, _ := reader.ReadString('\n')
			filename = strings.TrimSpace(filename)
			if filename == "" {
				filename = "volume_history.csv"
			}
			exportCSV(filename)
			continue
		} else if choice == "u" || choice == "U" {
			fmt.Println("Доступные единицы: куб. ед., см³, м³, дм³, л, in³")
			fmt.Print("Выберите единицы: ")
			input, _ := reader.ReadString('\n')
			input = strings.TrimSpace(input)
			if input != "" {
				units = input
			}
			continue
		} else if shape, ok := shapes[choice]; ok {
			fmt.Printf("\nФигура: %s\n", shape.Name)
			params := make([]float64, len(shape.Params))
			for i, pname := range shape.Params {
				params[i] = getFloat("Введите "+pname+": ", reader)
			}
			result := shape.Func(params)
			resultStr := fmt.Sprintf("%.4f %s", result, units)
			fmt.Printf("\nОбъём %s: %s\n", strings.ToLower(shape.Name), resultStr)

			fmt.Print("Сохранить результат? (y/n): ")
			saveChoice, _ := reader.ReadString('\n')
			saveChoice = strings.TrimSpace(strings.ToLower(saveChoice))
			if saveChoice == "y" {
				entry := HistoryEntry{
					Date:   time.Now().Format(time.RFC3339),
					Shape:  shape.Name,
					Params: strings.Join(strings.Fields(fmt.Sprint(params)), ", "),
					Result: resultStr,
					Units:  units,
				}
				saveHistory(entry)
				history = append(history, entry)
				fmt.Println("✅ Сохранено!")
			}
		} else {
			fmt.Println("Неверный выбор.")
		}
	}
}
