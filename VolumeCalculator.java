// VolumeCalculator.java - Калькулятор объёма тел на Java (CLI)
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.function.Function;

public class VolumeCalculator {
    private static final Scanner scanner = new Scanner(System.in);
    private static final String HISTORY_FILE = "volume_history.json";
    private static final double PI = Math.PI;

    static class Shape {
        String name;
        Function<List<Double>, Double> func;
        List<String> params;

        Shape(String name, Function<List<Double>, Double> func, String... params) {
            this.name = name;
            this.func = func;
            this.params = Arrays.asList(params);
        }
    }

    static class HistoryEntry {
        String date;
        String shape;
        String params;
        String result;
        String units;
    }

    private static final Map<String, Shape> shapes = new LinkedHashMap<>();

    static {
        shapes.put("1", new Shape("Куб", p -> Math.pow(p.get(0), 3), "сторону"));
        shapes.put("2", new Shape("Шар", p -> 4.0/3.0 * PI * Math.pow(p.get(0), 3), "радиус"));
        shapes.put("3", new Shape("Цилиндр", p -> PI * Math.pow(p.get(0), 2) * p.get(1), "радиус", "высоту"));
        shapes.put("4", new Shape("Конус", p -> 1.0/3.0 * PI * Math.pow(p.get(0), 2) * p.get(1), "радиус", "высоту"));
        shapes.put("5", new Shape("Параллелепипед", p -> p.get(0) * p.get(1) * p.get(2), "длину", "ширину", "высоту"));
        shapes.put("6", new Shape("Пирамида", p -> 1.0/3.0 * p.get(0) * p.get(1), "площадь основания", "высоту"));
        shapes.put("7", new Shape("Призма", p -> p.get(0) * p.get(1), "площадь основания", "высоту"));
        shapes.put("8", new Shape("Тор", p -> 2.0 * Math.pow(PI, 2) * p.get(0) * Math.pow(p.get(1), 2), "большой радиус", "малый радиус"));
        shapes.put("9", new Shape("Эллипсоид", p -> 4.0/3.0 * PI * p.get(0) * p.get(1) * p.get(2), "полуось a", "полуось b", "полуось c"));
        shapes.put("10", new Shape("Усечённый конус", p -> 1.0/3.0 * PI * p.get(2) * (Math.pow(p.get(0), 2) + p.get(0)*p.get(1) + Math.pow(p.get(1), 2)), "радиус 1", "радиус 2", "высоту"));
    }

    public static void saveHistory(HistoryEntry entry) {
        List<HistoryEntry> history = loadHistory();
        history.add(entry);
        try (PrintWriter pw = new PrintWriter(HISTORY_FILE)) {
            pw.println("[");
            for (int i = 0; i < history.size(); i++) {
                HistoryEntry e = history.get(i);
                pw.printf("  {\"date\":\"%s\",\"shape\":\"%s\",\"params\":\"%s\",\"result\":\"%s\",\"units\":\"%s\"}%s\n",
                        e.date, e.shape, e.params, e.result, e.units, (i < history.size() - 1 ? "," : ""));
            }
            pw.println("]");
        } catch (IOException ex) {}
    }

    public static List<HistoryEntry> loadHistory() {
        List<HistoryEntry> history = new ArrayList<>();
        try {
            String json = new String(Files.readAllBytes(Paths.get(HISTORY_FILE)));
            // Упрощённо: в реальном проекте использовать Jackson
        } catch (Exception e) {}
        return history;
    }

    public static void exportCSV(String filename) {
        List<HistoryEntry> history = loadHistory();
        if (history.isEmpty()) {
            System.out.println("История пуста.");
            return;
        }
        try (PrintWriter pw = new PrintWriter(filename)) {
            pw.println("Дата,Фигура,Параметры,Объём,Единицы");
            for (HistoryEntry e : history) {
                String units = e.units == null || e.units.isEmpty() ? "куб. ед." : e.units;
                pw.printf("%s,%s,\"%s\",%s,%s\n", e.date.substring(0,19), e.shape, e.params, e.result, units);
            }
            System.out.println("Экспортировано в " + filename);
        } catch (IOException ex) {
            System.out.println("Ошибка экспорта: " + ex.getMessage());
        }
    }

    public static double getDouble(String prompt) {
        while (true) {
            System.out.print(prompt);
            try {
                double val = Double.parseDouble(scanner.nextLine().trim());
                if (val > 0) return val;
                System.out.println("Введите положительное число.");
            } catch (NumberFormatException e) {
                System.out.println("Введите число.");
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("📦 КАЛЬКУЛЯТОР ОБЪЁМА ТЕЛ");
        List<HistoryEntry> history = loadHistory();
        String units = "куб. ед.";

        while (true) {
            System.out.println("\nВыберите фигуру:");
            for (Map.Entry<String, Shape> entry : shapes.entrySet()) {
                System.out.println(entry.getKey() + ". " + entry.getValue().name);
            }
            System.out.println("h. Показать историю");
            System.out.println("e. Экспорт CSV");
            System.out.println("u. Сменить единицы");
            System.out.println("0. Выход");

            String choice = scanner.nextLine().trim();

            if (choice.equals("0")) break;
            else if (choice.equalsIgnoreCase("h")) {
                if (history.isEmpty()) {
                    System.out.println("История пуста.");
                } else {
                    System.out.println("\n=== ИСТОРИЯ ===");
                    int start = Math.max(0, history.size() - 10);
                    for (int i = start; i < history.size(); i++) {
                        HistoryEntry e = history.get(i);
                        System.out.printf("%s | %s | %s\n", e.date.substring(0, 19), e.shape, e.result);
                    }
                }
                continue;
            } else if (choice.equalsIgnoreCase("e")) {
                System.out.print("Имя CSV файла (по умолчанию volume_history.csv): ");
                String filename = scanner.nextLine().trim();
                if (filename.isEmpty()) filename = "volume_history.csv";
                exportCSV(filename);
                continue;
            } else if (choice.equalsIgnoreCase("u")) {
                System.out.println("Доступные единицы: куб. ед., см³, м³, дм³, л, in³");
                System.out.print("Выберите единицы: ");
                String input = scanner.nextLine().trim();
                if (!input.isEmpty()) units = input;
                continue;
            } else if (shapes.containsKey(choice)) {
                Shape shape = shapes.get(choice);
                System.out.println("\nФигура: " + shape.name);
                List<Double> params = new ArrayList<>();
                for (String pname : shape.params) {
                    params.add(getDouble("Введите " + pname + ": "));
                }
                double result = shape.func.apply(params);
                String resultStr = String.format("%.4f %s", result, units);
                System.out.printf("\nОбъём %s: %s\n", shape.name.toLowerCase(), resultStr);

                System.out.print("Сохранить результат? (y/n): ");
                String save = scanner.nextLine().trim().toLowerCase();
                if (save.equals("y")) {
                    HistoryEntry entry = new HistoryEntry();
                    entry.date = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
                    entry.shape = shape.name;
                    entry.params = params.toString().replace("[", "").replace("]", "");
                    entry.result = resultStr;
                    entry.units = units;
                    saveHistory(entry);
                    history.add(entry);
                    System.out.println("✅ Сохранено!");
                }
            } else {
                System.out.println("Неверный выбор.");
            }
        }
    }
}
