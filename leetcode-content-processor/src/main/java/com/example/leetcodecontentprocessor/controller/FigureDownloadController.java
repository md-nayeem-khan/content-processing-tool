package com.example.leetcodecontentprocessor.controller;

import com.example.leetcodecontentprocessor.service.FigureDownloadService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class FigureDownloadController {

    private final FigureDownloadService figureDownloadService;

    @Autowired
    public FigureDownloadController(FigureDownloadService figureDownloadService) {
        this.figureDownloadService = figureDownloadService;
    }

    @PostMapping("/figure-download")
    public ResponseEntity<byte[]> downloadFiguresAndSlides(@RequestBody Map<String, List<String>> request) {
        try {
            List<String> questionSlugs = request.get("questionSlugs");
            byte[] zipData = figureDownloadService.downloadFiguresAndSlidesBySlugs(questionSlugs);

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=figures_and_slides.zip")
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .body(zipData);

        } catch (IOException e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}
