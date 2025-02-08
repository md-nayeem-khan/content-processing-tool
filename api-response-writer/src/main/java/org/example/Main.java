package org.example;

import java.nio.file.Paths;

public class Main {
    public static void main(String[] args) {
        String inputDir = "api-response-writer/input/";
        String outputDir = "api-response-writer/output/";

        ApiResponseProcessor apiResponseProcessor = new ApiResponseProcessor();
        apiResponseProcessor.processApiResponse(
                Paths.get(inputDir, "api-response.json").toString(),
                Paths.get(outputDir, "content.tex").toString()
        );
    }
}