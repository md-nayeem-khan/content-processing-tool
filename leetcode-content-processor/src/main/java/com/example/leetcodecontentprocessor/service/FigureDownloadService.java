package com.example.leetcodecontentprocessor.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StreamUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Service
public class FigureDownloadService {

    @Value("${graphql.csrftoken}")
    private String csrftoken;

    @Value("${graphql.leetcode.session}")
    private String leetcodeSession;

    private static final String IMG_TAG_REGEX = "!\\[([^\\]]+)\\]\\(\\.\\.\\/Figures\\/(.+?\\.(jpg|jpeg|png|gif|svg|PNG|JPG|JPEG|GIF|SVG))\\)";
    private static final String SLIDE_TAG_REGEX = "!?!\\.\\./Documents/(\\S+?):\\d+,\\d+!?!";
    private static final String GRAPHQL_URL = "https://leetcode.com/graphql/";
    private static final String GRAPHQL_QUERY = "{\"query\":\"\\n    query ugcArticleOfficialSolutionArticle($questionSlug: String!) {\\n  ugcArticleOfficialSolutionArticle(questionSlug: $questionSlug) {\\n    content\\n  }\\n}\\n    \",\"variables\":{\"questionSlug\":\"%s\"},\"operationName\":\"ugcArticleOfficialSolutionArticle\"}";
    private static final String QUESTION_CONTENT_GRAPHQL_QUERY = "{\"query\":\"\\n    query questionDetail($titleSlug: String!) {\\n  question(titleSlug: $titleSlug) {\\n    content\\n  }\\n}\\n    \",\"variables\":{\"titleSlug\":\"%s\"},\"operationName\":\"questionDetail\"}";

    private static final Logger logger = LoggerFactory.getLogger(FigureDownloadService.class);

    public byte[] downloadFiguresAndSlidesBySlugs(List<String> questionSlugs) throws IOException {
        logger.info("Method {} begins.", "downloadFiguresAndSlidesBySlugs");
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();

        try (ZipOutputStream zipOutputStream = new ZipOutputStream(byteArrayOutputStream)) {
            for (String questionSlug : questionSlugs) {
                logger.info("Started processing content with question slug: {}", questionSlug);
                String solutionContent = fetchSolutionContent(questionSlug);
                String questionContent = fetchQuestionContent(questionSlug);
                int imageCounter = 1;
                int slideCounter = 1;
                if (solutionContent != null && !solutionContent.isEmpty()) {
                    Pattern imgPattern = Pattern.compile(IMG_TAG_REGEX);
                    Matcher imgMatcher = imgPattern.matcher(solutionContent);

                    while (imgMatcher.find()) {
                        String imagePath = imgMatcher.group(2);
                        String extension = imagePath.substring(imagePath.lastIndexOf('.'));
                        logger.info("Found image path: {} for question slug: {}", imagePath, questionSlug);
                        String imageUrl = "https://assets.leetcode.com/static_assets/media/original_images/" + imagePath;
                        String sequentialImageName = questionSlug + "/" + imageCounter++ + extension;

                        addImageToZip(imageUrl, zipOutputStream, sequentialImageName);
                    }

                    Pattern slidePattern = Pattern.compile(SLIDE_TAG_REGEX);
                    Matcher slideMatcher = slidePattern.matcher(solutionContent);

                    while (slideMatcher.find()) {
                        String jsonFileName = slideMatcher.group(1);
                        String jsonUrl = "https://assets.leetcode.com/static_assets/media/documents/" + jsonFileName;

                        String jsonResponse = fetchJson(jsonUrl);
                        if (jsonResponse == null) {
                            continue;
                        }

                        Pattern slideImagePattern = Pattern.compile("\\.\\./Figures/(.+?\\.(jpg|jpeg|png|gif|svg|PNG|JPG|JPEG|GIF|SVG))");
                        Matcher slideImageMatcher = slideImagePattern.matcher(jsonResponse);

                        int slideImageCounter = 1;
                        while (slideImageMatcher.find()) {
                            String slideImagePath = slideImageMatcher.group(1);
                            String extension = slideImagePath.substring(slideImagePath.lastIndexOf('.'));
                            String slideImageUrl = "https://assets.leetcode.com/static_assets/media/original_images/" + slideImagePath;

                            String slideImageName = questionSlug + "/slide-" + slideCounter + "-image-" + slideImageCounter++ + extension;
                            addImageToZip(slideImageUrl, zipOutputStream, slideImageName);
                        }
                        slideCounter++;
                    }
                }

                if (questionContent != null && !questionContent.isEmpty()) {
                    Pattern imgPattern = Pattern.compile("<img[^>]*src=\\\"(.*?)\\\"[^>]*>");
                    Matcher imgMatcher = imgPattern.matcher(questionContent);

                    while (imgMatcher.find()) {
                        String imageUrl = imgMatcher.group(1);
                        String extension = imageUrl.substring(imageUrl.lastIndexOf('.'));
                        logger.info("Found image url: {} for question slug: {}", imageUrl, questionSlug);
                        String sequentialImageName = questionSlug + "/" + imageCounter++ + extension;

                        addImageToZip(imageUrl, zipOutputStream, sequentialImageName);
                    }
                }
            }
        }

        return byteArrayOutputStream.toByteArray();
    }

    private String fetchSolutionContent(String questionSlug) {
        logger.info("Method {} begins.", "fetchSolutionContent");
        try {
            logger.info("Fetching solution content with question slug: {}", questionSlug);
            URL url = new URL(GRAPHQL_URL);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("x-csrftoken", csrftoken);
            connection.setRequestProperty("Cookie", "LEETCODE_SESSION=" + leetcodeSession);
            connection.setDoOutput(true);
            OutputStream os = connection.getOutputStream();
            byte[] input = String.format(GRAPHQL_QUERY, questionSlug).getBytes();
            os.write(input, 0, input.length);

            InputStream inputStream = connection.getInputStream();
            String jsonResponse = new String(inputStream.readAllBytes());
            JsonNode root = new ObjectMapper().readTree(jsonResponse);
            return root.path("data").path("ugcArticleOfficialSolutionArticle").path("content").asText();
        } catch (IOException e) {
            logger.error("Error occurred while processing content for question slug: {}. Error details: {}", questionSlug, e.getMessage());
        }
        return null;
    }

    private String fetchQuestionContent(String questionSlug) {
        logger.info("Method {} begins.", "fetchQuestionContent");
        try {
            logger.info("Fetching question content with question slug: {}", questionSlug);
            URL url = new URL(GRAPHQL_URL);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("x-csrftoken", csrftoken);
            connection.setRequestProperty("Cookie", "LEETCODE_SESSION=" + leetcodeSession);
            connection.setDoOutput(true);
            OutputStream os = connection.getOutputStream();
            byte[] input = String.format(QUESTION_CONTENT_GRAPHQL_QUERY, questionSlug).getBytes();
            os.write(input, 0, input.length);

            InputStream inputStream = connection.getInputStream();
            String jsonResponse = new String(inputStream.readAllBytes());
            JsonNode root = new ObjectMapper().readTree(jsonResponse);
            return root.path("data").path("question").path("content").asText();
        } catch (IOException e) {
            logger.error("Error occurred while processing content for question slug: {}. Error details: {}", questionSlug, e.getMessage());
        }
        return null;
    }

    private void addImageToZip(String imageUrl, ZipOutputStream zipOutputStream, String fileName) {
        logger.info("Method addImageToZip begins");
        try {
            logger.info("Fetching image with image url: {}", imageUrl);
            URL url = new URL(imageUrl);
            zipOutputStream.putNextEntry(new ZipEntry(fileName));
            InputStream inputStream = url.openStream();
            StreamUtils.copy(inputStream, zipOutputStream);
            zipOutputStream.closeEntry();
        } catch (IOException e) {
            logger.error("Error occurred while fetching image from URL: {}. Error details: {}", imageUrl, e.getMessage());
        }
    }

    private String fetchJson(String jsonUrl) {
        logger.info("Method fetchJson begins");
        try {
            logger.info("Fetching json with json url: {}", jsonUrl);
            URL url = new URL(jsonUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            InputStream inputStream = connection.getInputStream();
            return new String(inputStream.readAllBytes());
        } catch (IOException e) {
            logger.error("Error occurred while fetching JSON from URL: {}. Error details: {}", jsonUrl, e.getMessage());
        }
        return null;
    }
}

