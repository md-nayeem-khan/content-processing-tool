package org.example;

import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

class ApiResponseProcessor {
    public void processApiResponse(String inputFilePath, String outputFilePath) {
        try (FileReader reader = new FileReader(inputFilePath)) {
            JSONTokener tokener = new JSONTokener(reader);
            JSONObject jsonObject = new JSONObject(tokener);

            String content = jsonObject.getString("content");

            try (FileWriter writer = new FileWriter(outputFilePath)) {
                writer.write(content);
                System.out.println("Content successfully written to " + outputFilePath);
            }
        } catch (IOException e) {
            System.err.println("Error reading or writing file: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Error processing JSON: " + e.getMessage());
        }
    }
}