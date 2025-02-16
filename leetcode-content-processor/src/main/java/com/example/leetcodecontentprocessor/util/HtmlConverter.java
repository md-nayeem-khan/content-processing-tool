package com.example.leetcodecontentprocessor.util;

import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStreamReader;

@Service
public class HtmlConverter {

    public String convertToLatex(String htmlContent) {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("pandoc", "-f", "html", "-t", "latex");
            Process process = processBuilder.start();

            process.getOutputStream().write(htmlContent.getBytes());
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
            return "Error converting HTML to LaTeX: " + e.getMessage();
        }
    }
}
