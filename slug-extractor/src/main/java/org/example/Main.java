package org.example;

import java.nio.file.Paths;

public class Main {
    public static void main(String[] args) {
        String inputDir = "slug-extractor/input/";
        String outputDir = "slug-extractor/output/";

        QuestionSlugExtractor questionSlugExtractor = new QuestionSlugExtractor();
        questionSlugExtractor.processQuestionUrls(
                Paths.get(inputDir, "questions.txt").toString(),
                Paths.get(outputDir, "api-request.json").toString()
        );
    }
}