package com.example.leetcodecontentprocessor.service;

import com.example.leetcodecontentprocessor.dto.SolutionData;
import com.example.leetcodecontentprocessor.util.ContentSanitizer;
import com.example.leetcodecontentprocessor.util.HtmlConverter;
import com.example.leetcodecontentprocessor.util.MarkdownConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import com.example.leetcodecontentprocessor.dto.ContentResponseDTO;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class ContentService {

    private final RestTemplate restTemplate;
    private final ContentSanitizer contentSanitizer;
    private final MarkdownConverter markdownConverter;
    private final HtmlConverter htmlConverter;

    private static final String GRAPHQL_ENDPOINT = "https://leetcode.com/graphql";

    @Value("${graphql.csrftoken}")
    private String csrftoken;

    @Value("${graphql.leetcode.session}")
    private String leetcodeSession;

    public ContentService(ContentSanitizer contentSanitizer, MarkdownConverter markdownConverter, HtmlConverter htmlConverter) {
        this.restTemplate = new RestTemplate();
        this.contentSanitizer = contentSanitizer;
        this.markdownConverter = markdownConverter;
        this.htmlConverter = htmlConverter;
    }

    public ContentResponseDTO processContent(List<String> questionSlugs) {
        StringBuilder mergedContent = new StringBuilder();

        questionSlugs.forEach(slug -> {
            String solutionMarkDownContent = fetchSolutionContent(slug);
            JsonNode questionData = new ObjectMapper().createObjectNode();

            try {
                questionData = new ObjectMapper().readTree(fetchQuestionContent(slug));
            } catch (Exception e) {
                e.printStackTrace();
            }

            String questionContent = convertHtmlContent(questionData.path("content").asText(), questionData.path("title").asText());

            List<String> codes = extractAndFetchIframeCodes(solutionMarkDownContent);
            List<String> figures = extractFigures(solutionMarkDownContent, slug);
            List<List<String>> slides = extractSlides(solutionMarkDownContent, slug);

            String solutionContent = convertMarkdownContent(solutionMarkDownContent, codes, slides, figures);

            SolutionData solutionData = new SolutionData(solutionContent, codes, figures, slides);

            mergedContent.append(questionContent).append("\n\n").append(solutionData.getContent()).append("\n\n");
        });

        return new ContentResponseDTO(mergedContent.toString());
    }

    private String convertMarkdownContent(String content, List<String> codes, List<List<String>> slides, List<String> figures) {
        String sanitizedContent = contentSanitizer.sanitizeSolution(content);
        String latexContent = markdownConverter.convertToLatex(sanitizedContent);
        String sanitizeLatexSolution = contentSanitizer.sanitizeLatexSolution(latexContent);
        String sanitizeLatexSolutionWithCodes = contentSanitizer.insertIframeCodes(sanitizeLatexSolution, codes);
        String sanitizeLatexSolutionWithFigures = contentSanitizer.insertFigures(sanitizeLatexSolutionWithCodes, figures);
        String sanitizeLatexSolutionWithSlides = contentSanitizer.insertSlides(sanitizeLatexSolutionWithFigures, slides);
        return sanitizeLatexSolutionWithSlides;
    }

    private String convertHtmlContent(String content, String questionTitle) {
        String sanitizedContent = contentSanitizer.sanitizeQuestion(content);
        String latexContent = htmlConverter.convertToLatex(sanitizedContent);
        return contentSanitizer.sanitizeLatexQuestion(latexContent, questionTitle);
    }

    private String fetchSolutionContent(String questionSlug) {
        String query = "query ugcArticleOfficialSolutionArticle($questionSlug: String!) { " +
                "ugcArticleOfficialSolutionArticle(questionSlug: $questionSlug) { content } }";

        String variables = "{ \"questionSlug\": \"" + questionSlug + "\" }";
        String payload = "{ \"operationName\": \"ugcArticleOfficialSolutionArticle\", \"query\": \"" + query + "\", \"variables\": " + variables + " }";

        return sendGraphQLRequest(payload, "ugcArticleOfficialSolutionArticle", "content");
    }

    private String fetchQuestionContent(String titleSlug) {
        String query = "query questionDetail($titleSlug: String!) { " +
                "question(titleSlug: $titleSlug) { title titleSlug content } }";

        String variables = "{ \"titleSlug\": \"" + titleSlug + "\" }";
        String payload = "{ \"operationName\": \"questionDetail\", \"query\": \"" + query + "\", \"variables\": " + variables + " }";

        return sendGraphQLRequest(payload, "question", null);
    }

    private String sendGraphQLRequest(String payload, String dataKey, String contentKey) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.add("Cookie", "csrftoken=" + csrftoken + "; LEETCODE_SESSION=" + leetcodeSession);

        HttpEntity<String> entity = new HttpEntity<>(payload, headers);
        ResponseEntity<String> response = restTemplate.exchange(GRAPHQL_ENDPOINT, HttpMethod.POST, entity, String.class);

        return parseGraphQLResponse(response.getBody(), dataKey, contentKey);
    }

    private String parseGraphQLResponse(String responseBody, String dataKey, String contentKey) {
        try {
            JsonNode root = new ObjectMapper().readTree(responseBody);
            JsonNode dataNode = root.path("data").path(dataKey);

            if (contentKey != null) {
                dataNode = dataNode.path(contentKey);
            }

            if (dataNode.isMissingNode() || dataNode.isNull()) {
                return "No content found or invalid response.";
            }

            return dataNode.toPrettyString();
        } catch (Exception e) {
            return "Error parsing GraphQL response: " + e.getMessage();
        }
    }

    private List<String> extractAndFetchIframeCodes(String solutionContent) {
        List<String> codes = new ArrayList<>();
        Pattern pattern = Pattern.compile("<iframe[^>]*src=\\\\?\"(https://leetcode\\.com/playground/([^\"]+))/shared\\\\?\"[^>]*>");
        Matcher matcher = pattern.matcher(solutionContent);

        while (matcher.find()) {
            String src = matcher.group(1);
            String uuid = matcher.group(2);

            String query = "query fetchPlayground {\\n" +
                    "  playground(uuid: \\\"" + uuid + "\\\") {\\n" +
                    "    testcaseInput\\n    name\\n    isUserOwner\\n    isLive\\n    showRunCode\\n    showOpenInPlayground\\n    selectedLangSlug\\n    isShared\\n    __typename\\n  }\\n" +
                    "  allPlaygroundCodes(uuid: \\\"" + uuid + "\\\") {\\n" +
                    "    code\\n    langSlug\\n    __typename\\n  }\\n}";

            String payload = "{ \"operationName\": \"fetchPlayground\", \"query\": \"" + query + "\", \"variables\": {} }";
            String response = sendGraphQLRequest(payload, "allPlaygroundCodes", null);

            try {
                JsonNode codesNode = new ObjectMapper().readTree(response);
                for (JsonNode codeNode : codesNode) {
                    if ("java".equals(codeNode.path("langSlug").asText())) {
                        codes.add(codeNode.path("code").asText());
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return codes;
    }

    private List<String> extractFigures(String solutionContent, String questionSlug) {
        List<String> figures = new ArrayList<>();
        Pattern pattern = Pattern.compile("!\\[([^\\]]+)\\]\\(\\.\\.\\/Figures\\/(.+?\\.(jpg|jpeg|png|gif|svg|PNG|JPG|JPEG|GIF|SVG))\\)");
        Matcher matcher = pattern.matcher(solutionContent);

        int imageCounter = 0;
        while (matcher.find()) {
            imageCounter++;
            String imageExtension = matcher.group(3);
            figures.add("images/" + questionSlug + "/" + imageCounter + "." + imageExtension);
        }
        return figures;
    }

    private List<List<String>> extractSlides(String solutionContent, String questionSlug) {
        List<List<String>> slides = new ArrayList<>();
        Pattern pattern = Pattern.compile("!?!\\.\\./Documents/(\\S+?):\\d+,\\d+!?!");
        Matcher matcher = pattern.matcher(solutionContent);

        int slideCounter = 0;
        while (matcher.find()) {
            slideCounter++;
            String source = matcher.group(1);
            String url = "https://assets.leetcode.com/static_assets/media/documents/" + source;

            try {
                String jsonResponse = restTemplate.getForObject(url, String.class);
                JsonNode slidesData = new ObjectMapper().readTree(jsonResponse).path("timeline");
                List<String> slideContent = new ArrayList<>();

                int imageCounter = 0;
                Pattern imgPattern = Pattern.compile("\\.\\./Figures/(.+?\\.(jpg|jpeg|png|gif|svg|PNG|JPG|JPEG|GIF|SVG))");

                for (JsonNode slideNode : slidesData) {
                    Matcher imgMatcher = imgPattern.matcher(slideNode.path("image").asText());
                    if (imgMatcher.find()) {
                        imageCounter++;
                        String imageExtension = imgMatcher.group(2);
                        slideContent.add("images/" +questionSlug + "/slide-" + slideCounter + "-image-" + imageCounter + "." + imageExtension);
                    }
                }
                slides.add(slideContent);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return slides;
    }
}
