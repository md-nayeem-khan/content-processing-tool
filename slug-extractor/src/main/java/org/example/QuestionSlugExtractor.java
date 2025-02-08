package org.example;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

class QuestionSlugExtractor {
    public void processQuestionUrls(String inputFilePath, String outputFilePath) {
        List<String> slugs = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(inputFilePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String slug = extractSlugFromUrl(line);
                if (slug != null && !slug.isEmpty()) {
                    slugs.add(slug);
                }
            }

            JSONObject jsonObject = new JSONObject();
            jsonObject.put("questionSlugs", new JSONArray(slugs));

            try (FileWriter writer = new FileWriter(outputFilePath)) {
                writer.write(jsonObject.toString(4));
                System.out.println("Question slugs successfully written to " + outputFilePath);
            }
        } catch (IOException e) {
            System.err.println("Error reading or writing file: " + e.getMessage());
        }
    }

    private String extractSlugFromUrl(String url) {
        if (url != null && url.contains("/problems/")) {
            String[] parts = url.split("/problems/");
            if (parts.length > 1) {
                String slugPart = parts[1];
                return slugPart.split("/")[0];
            }
        }
        return "";
    }
}


