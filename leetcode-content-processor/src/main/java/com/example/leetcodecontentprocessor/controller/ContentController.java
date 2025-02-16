package com.example.leetcodecontentprocessor.controller;

import com.example.leetcodecontentprocessor.dto.ContentResponseDTO;
import com.example.leetcodecontentprocessor.service.ContentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/content")
public class ContentController {

    private final ContentService contentService;

    @Autowired
    public ContentController(ContentService contentService) {
        this.contentService = contentService;
    }

    @PostMapping("/process-content")
    public ResponseEntity<ContentResponseDTO> processContent(@RequestBody Map<String, List<String>> payload) {
        List<String> questionSlugs = payload.get("questionSlugs");
        ContentResponseDTO processedContent = contentService.processContent(questionSlugs);
        return ResponseEntity.ok(processedContent);
    }
}
