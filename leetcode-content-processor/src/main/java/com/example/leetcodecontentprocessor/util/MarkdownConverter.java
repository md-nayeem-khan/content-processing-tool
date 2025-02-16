package com.example.leetcodecontentprocessor.util;

import org.springframework.stereotype.Component;
import java.io.BufferedReader;
import java.io.InputStreamReader;

@Component
public class MarkdownConverter {

    public String convertToLatex(String markdownContent) {
        if (markdownContent == null || markdownContent.isEmpty()) return "";

        try {
            ProcessBuilder processBuilder = new ProcessBuilder("pandoc", "-f", "markdown", "-t", "latex");
            Process process = processBuilder.start();

            process.getOutputStream().write(markdownContent.getBytes());
            process.getOutputStream().close();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder latexContent = new StringBuilder();
            String line;

            while ((line = reader.readLine()) != null) {
                latexContent.append(line).append("\n");
            }

            process.waitFor();
            return latexContent.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return "Error converting markdown to LaTeX: " + e.getMessage();
        }
    }
}
