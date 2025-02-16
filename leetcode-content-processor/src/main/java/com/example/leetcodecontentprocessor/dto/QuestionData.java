package com.example.leetcodecontentprocessor.dto;

public class QuestionData {
    private final String title;
    private final String content;

    public QuestionData(String title, String content) {
        this.title = title;
        this.content = content;
    }

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }
}