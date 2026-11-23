// Top 10 most common words in words.txt
import java.nio.file.*;
import java.util.*;

public class WordFreq {
    public static void main(String[] args) throws Exception {
        String text = Files.readString(Path.of("words.txt"));
        Map<String, Integer> counts = new HashMap<>();
        for (String word : text.split("\\s+")) {
            if (!word.isEmpty()) counts.merge(word, 1, Integer::sum);
        }

        counts.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed()
                    .thenComparing(Map.Entry.comparingByKey()))
            .limit(10)
            .forEach(e -> System.out.println(e.getKey() + " " + e.getValue()));
    }
}
