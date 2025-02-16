package com.example.leetcodecontentprocessor.dto;

import java.util.List;

public class SolutionData {
    private String content;
    private List<String> codes;
    private List<String> figures;
    private List<List<String>> slides;

    public SolutionData(String content, List<String> codes, List<String> figures, List<List<String>> slides) {
        this.content = content;
        this.codes = codes;
        this.figures = figures;
        this.slides = slides;
    }

    public String getContent() {
        return content;
    }

    public List<String> getCodes() {
        return codes;
    }

    public List<String> getFigures() {
        return figures;
    }

    public List<List<String>> getSlides() {
        return slides;
    }
}