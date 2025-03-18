package com.example.leetcodecontentprocessor.util;

import org.springframework.stereotype.Component;

import java.util.Iterator;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Component
public class ContentSanitizer {

    public String sanitizeSolution(String solution) {
        if (solution == null || solution.isEmpty()) {
            return solution;
        }

        solution = solution.trim();

        if (solution.startsWith("\"")) {
            solution = solution.substring(1);
        }
        if (solution.endsWith(";")) {
            solution = solution.substring(0, solution.length() - 1);
        }
        if (solution.endsWith(",")) {
            solution = solution.substring(0, solution.length() - 1);
        }
        if (solution.endsWith("\"")) {
            solution = solution.substring(0, solution.length() - 1);
        }
        String figurePattern = "!\\[([^\\]]+)\\]\\(\\.\\.\\/Figures\\/(.+?\\.(jpg|jpeg|png|gif|svg|PNG|JPG|JPEG|GIF|SVG))\\)";
        String svgFigurePattern = "!\\[([^\\]]+)\\]\\(\\.\\.\\/Documents\\/(.+?\\.(jpg|jpeg|png|gif|svg|PNG|JPG|JPEG|GIF|SVG))\\)";
        solution = solution.replaceAll(figurePattern, "!Flag content for figure!");
        solution = solution.replaceAll(svgFigurePattern, "!Flag content for svg figure!");

//        String figureWithLabelPattern = "!\\[([^\\]]+)\\]\\(\\.\\.\\/Figures\\/(.+?\\.(jpg|jpeg|png|gif|svg|PNG|JPG|JPEG|GIF|SVG))\\)\\n\\*[^\\*]+\\*";
//        solution = solution.replaceAll(figureWithLabelPattern, "> Flag content for figure");

        String exclPattern = "!\\?!\\.\\..*?!\\?!";
        solution = solution.replaceAll(exclPattern, "!Flag content for slides!");

        String divRegex = "<div[^>]*?>.*?</div>";
        solution = solution.replaceAll(divRegex, "");

        String iframeRegex = "<iframe[^>]*?>.*?</iframe>";
        String iframeReplacement = "!Flag content for code!";

        solution = solution.replaceAll(iframeRegex, iframeReplacement);

        solution = solution.replace("[TOC]", "");

        solution = solution.replace("\\r\\n", "\n");

        solution = solution.replace("\\n", "\n");
        solution = solution.replace("$$", "$");

        solution = solution.replace("---", "");

        Pattern pattern = Pattern.compile("\\$([^$]*)\\$");
        Matcher matcher = pattern.matcher(solution);

        StringBuilder result = new StringBuilder();
        while (matcher.find()) {
            String content = matcher.group(1);
            content = content.replace("//", "/");
            matcher.appendReplacement(result, "\\$" + content + "\\$");
        }
        matcher.appendTail(result);

        solution = result.toString();
        return solution;
    }

    public String sanitizeQuestion(String question) {
        if (question == null || question.isEmpty()) {
            return question;
        }

        question = question.trim();

        if (question.startsWith("\"")) {
            question = question.substring(1);
        }
        if (question.endsWith(";")) {
            question = question.substring(0, question.length() - 1);
        }
        if (question.endsWith(",")) {
            question = question.substring(0, question.length() - 1);
        }
        if (question.endsWith("\"")) {
            question = question.substring(0, question.length() - 1);
        }

        Pattern pattern = Pattern.compile("\\\\u([0-9a-fA-F]{4})");
        Matcher matcher = pattern.matcher(question);

        StringBuilder decodedString = new StringBuilder();

        while (matcher.find()) {
            String hexCode = matcher.group(1);
            matcher.appendReplacement(decodedString, String.valueOf((char) Integer.parseInt(hexCode, 16)));
        }

        matcher.appendTail(decodedString);

        question = decodedString.toString();

        String figurePattern = "<img\\s+[^>]*?src\\s*=\\s*(['\"])(.*?)\\1[^>]*?>";
        question = question.replaceAll(figurePattern, "!Flag content for figure!");

        question = question.replace("\\n", "\n");
        question = question.replace("\\t", "\n");

        return question;
    }

    public String sanitizeLatexSolution(String latexContent) {
        Pattern videoSolutionPattern = Pattern.compile("\\{Video Solution\\}");
        Pattern targetLinePattern = Pattern.compile(
                "(\\\\subsection|\\\\subsubsection|\\\\end\\{itemize\\}|\\\\end\\{quote\\}|\\\\begin\\{itemize\\}|\\\\end\\{verbatim\\}|\\\\begin\\{verbatim\\}|\\\\begin\\{quote\\}|\\\\begin\\{enumerate\\}|\\\\end\\{enumerate\\}|\\\\begin\\{lstlisting\\}|\\\\end\\{lstlisting\\})"
        );
        Pattern intuitionPattern = Pattern.compile("\\{(Intuition)\\}");
        Pattern algorithmPattern = Pattern.compile("\\{(Algorithm)\\}");
        Pattern tightListPattern = Pattern.compile("tightlist");
        Pattern paragraphPattern = Pattern.compile("\\\\paragraph\\{([^}]*)}\\s*\\\\label\\{([^}]*)}\\s*");
        Pattern conjugativeSubsectionPattern = Pattern.compile("([^}]*)}\\s*\\\\label\\{([^}]*)}\\s*");

//        Pattern blockPattern = Pattern.compile(
//                "\\\\begin\\{quote\\}\\R\\*\\*\\* Find the solution from src folder\\R\\\\end\\{quote\\}",
//                Pattern.MULTILINE
//        );
//
//        Pattern slidePattern = Pattern.compile(
//                "\\\\begin\\{quote\\}\\RFlag content for slides\\R\\\\end\\{quote\\}",
//                Pattern.MULTILINE
//        );
//
//        Pattern figurePattern = Pattern.compile(
//                "\\\\begin\\{quote\\}\\RFlag content for figure\\R\\\\end\\{quote\\}",
//                Pattern.MULTILINE
//        );
//
//        String slidePatternReplacement = """
//                \\\\begin{slides}
//                Flag content for slides
//                \\\\end{slides}""";
//
//        String figurePatternReplacement = """
//                \\\\begin{single-figure}
//                Flag content for figure
//                \\\\end{single-figure}""";
//
//        String blockPatternReplacement = """
//                \\\\begin{lstlisting}
//                public boolean methodName() {
//                    return false;
//                }
//                \\\\end{lstlisting}""";
//
//        latexContent = blockPattern.matcher(latexContent).replaceAll(blockPatternReplacement);
//        latexContent = figurePattern.matcher(latexContent).replaceAll(figurePatternReplacement);
//        latexContent = slidePattern.matcher(latexContent).replaceAll(slidePatternReplacement);
        // did change
    //    latexContent = latexContent.replace("!Flag content for math!", "$");
        // did change
      //  latexContent = latexContent.replace("\\textbackslash{}", "");
        // did change
      //  latexContent = latexContent.replace("\\textbackslash ", "\\");

        String[] lines = latexContent.split("\n");

        StringBuilder modifiedContent = new StringBuilder();

        boolean previousMatched = false;
        String previousLine = null;

        for (String line : lines) {
            Matcher videoMatcher = videoSolutionPattern.matcher(line);
            Matcher targetMatcher = targetLinePattern.matcher(line);
            Matcher intuitionMatcher = intuitionPattern.matcher(line);
            Matcher algorithmMatcher = algorithmPattern.matcher(line);
            Matcher tightListMatcher = tightListPattern.matcher(line);
            Matcher paragraphMatcher = paragraphPattern.matcher(line);
            Matcher conjugativeSubsectionMatcher = conjugativeSubsectionPattern.matcher(line);

            if (tightListMatcher.find()) {
                continue;
            }

            if (videoMatcher.find()) {
                previousMatched = true;
                continue;
            }

            if (paragraphMatcher.find()) {
                line = paragraphMatcher.replaceAll("\\\\textbf{$1}");
            }

            if (targetMatcher.find()) {
                if (line.contains("{Solution Article}") || (line.contains("{Solution}")) && line.startsWith("\\subsection")) {
                    line = line.replaceFirst("^\\\\subsection", "\\\\subsubsection");
                }
                if (previousLine != null && previousLine.trim().isEmpty()) {
                    int lastLineIndex = modifiedContent.lastIndexOf("\n");
                    if (lastLineIndex != -1) {
                        int secondLastLineIndex = modifiedContent.lastIndexOf("\n", lastLineIndex - 1);
                        if (secondLastLineIndex != -1) {
                            modifiedContent.delete(secondLastLineIndex + "\n".length(), lastLineIndex + "\n".length());
                        }
                    }
                }
                previousMatched = true;
                modifiedContent.append(line).append("\n");
                previousLine = line;
                continue;
            }

            if (previousMatched && line.trim().isEmpty()) {
                previousMatched = false;
                continue;
            }

            if (intuitionMatcher.find()) {
                //  modifiedContent.append(line).append("\n").append("\\\\").append("\n");
                modifiedContent.append(line).append("\n");
                previousLine = line;
                continue;
            }

            if (algorithmMatcher.find()) {
                modifiedContent.append("\\\\").append("\n").append(line).append("\n");
                previousLine = line;
                continue;
            }

            if (previousMatched && !line.trim().isEmpty() && !conjugativeSubsectionMatcher.find()) {
                previousMatched = false;
            }

            if (line.trim().isEmpty()) {
                modifiedContent.append("\\\\").append("\n");
            } else {
                modifiedContent.append(line).append("\n");
            }
            previousLine = line;
        }

        modifiedContent.append("\n").append("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%");

        return modifiedContent.toString().trim();
    }

    public String sanitizeLatexQuestion(String latexContent, String questionTitle) {
        Pattern targetLinePattern = Pattern.compile(
                "(\\\\subsection|\\\\subsubsection|\\\\end\\{itemize\\}|\\\\end\\{quote\\}|\\\\begin\\{itemize\\}|\\\\end\\{verbatim\\}|\\\\begin\\{verbatim\\}|\\\\begin\\{quote\\}|\\\\begin\\{enumerate\\}|\\\\end\\{enumerate\\}|\\\\begin\\{lstlisting\\}|\\\\end\\{lstlisting\\})"
        );
        Pattern tightListPattern = Pattern.compile("tightlist");
        String[] lines = latexContent.split("\n");

        StringBuilder modifiedContent = new StringBuilder();

        boolean previousMatched = false;
        String previousLine = null;

        modifiedContent.append("\\subsection{").append(questionTitle).append("}").append("\n");
        modifiedContent.append("\\subsubsection{Description}").append("\n");

        for (String line : lines) {
            Matcher targetMatcher = targetLinePattern.matcher(line);
            Matcher tightListMatcher = tightListPattern.matcher(line);

            if (tightListMatcher.find()) {
                continue;
            }
            if (targetMatcher.find()) {
                if (previousLine != null && previousLine.trim().isEmpty()) {
                    int lastLineIndex = modifiedContent.lastIndexOf("\n");
                    if (lastLineIndex != -1) {
                        int secondLastLineIndex = modifiedContent.lastIndexOf("\n", lastLineIndex - 1);
                        if (secondLastLineIndex != -1) {
                            modifiedContent.delete(secondLastLineIndex + "\n".length(), lastLineIndex + "\n".length());
                        }
                    }
                }
                modifiedContent.append(line).append("\n");
                previousMatched = true;
                previousLine = line;
                continue;
            }

            if (previousMatched && line.trim().isEmpty()) {
                previousMatched = false;
                continue;
            }

            if (!line.trim().isEmpty()) {
                previousMatched = false;
            }

            if (line.trim().isEmpty()) {
                modifiedContent.append("\\\\").append("\n");
            } else {
                modifiedContent.append(line).append("\n");
            }
            previousLine = line;
        }

        return modifiedContent.toString().trim();
    }

    public String insertIframeCodes(String content, List<String> codes) {
//        Pattern pattern = Pattern.compile("\\\\begin\\{lstlisting\\}([\\s\\S]*?)\\\\end\\{lstlisting\\}", Pattern.DOTALL);
        Pattern pattern = Pattern.compile("!Flag content for code!");

        Matcher matcher = pattern.matcher(content);

        Iterator<String> codeIterator = codes.iterator();
        StringBuffer updatedContent = new StringBuffer();

        while (matcher.find() && codeIterator.hasNext()) {
            String code = codeIterator.next();
            String replacement = "\\begin{lstlisting}" + "\n" + code + "\n" + "\\end{lstlisting}";
            matcher.appendReplacement(updatedContent, Matcher.quoteReplacement(replacement));
        }
        matcher.appendTail(updatedContent);

        return updatedContent.toString();
    }

    public String insertFigures(String content, List<String> figures) {
        //Pattern pattern = Pattern.compile("\\\\begin\\{single-figure\\}([\\s\\S]*?)Flag content for figure([\\s\\S]*?)\\\\end\\{single-figure\\}", Pattern.DOTALL);
        Pattern figurePattern = Pattern.compile("!Flag content for figure!");
        Matcher figureMatcher = figurePattern.matcher(content);

        StringBuffer updatedContent = new StringBuffer();
        Iterator<String> figureIterator = figures.iterator();

        while (figureMatcher.find() && figureIterator.hasNext()) {
            String figure = figureIterator.next();
            String replacement = "\\begin{figure}[htbp]\n" +
                    "    \\centering\n" +
                    "    \\includegraphics[width=0.65\\textwidth]{" + figure + "}\n" +
                    "\\end{figure}";
            figureMatcher.appendReplacement(updatedContent, Matcher.quoteReplacement(replacement));
        }
        figureMatcher.appendTail(updatedContent);

        String modifiedContent = updatedContent.toString();
        Pattern svgFigurePattern = Pattern.compile("!Flag content for svg figure!");
        Matcher svgFigureMatcher = svgFigurePattern.matcher(modifiedContent);
        StringBuffer finalContent = new StringBuffer();

        while (svgFigureMatcher.find() && figureIterator.hasNext()) {
            String figure = figureIterator.next();
            String replacement = "\\begin{figure}[htbp]\n" +
                    "    \\centering\n" +
                    "    \\includegraphics[width=0.65\\textwidth]{" + figure + "}\n" +
                    "\\end{figure}";
            svgFigureMatcher.appendReplacement(finalContent, Matcher.quoteReplacement(replacement));
        }
        svgFigureMatcher.appendTail(finalContent);

        return finalContent.toString();
    }

    public String insertSlides(String content, List<List<String>> slides) {
        Pattern pattern = Pattern.compile("!Flag content for slides!");

        Matcher matcher = pattern.matcher(content);

        StringBuffer updatedContent = new StringBuffer();
        int slideCounter = 1;

        while (matcher.find() && slideCounter <= slides.size()) {
            List<String> slideImages = slides.get(slideCounter - 1);
            StringBuilder slideContent = new StringBuilder();

            for (int i = 0; i < slideImages.size(); i += 2) {
                if (i + 1 < slideImages.size()) {
                    slideContent.append("\\begin{figure}[htbp]\n")
                            .append("    \\centering\n")
                            .append("    \\begin{subfigure}[b]{0.48\\textwidth}\n")
                            .append("        \\centering\n")
                            .append("        \\includegraphics[width=\\textwidth]{")
                            .append(slideImages.get(i))
                            .append("}\n")
                            .append("    \\end{subfigure}\n")
                            .append("    \\hfill\n")
                            .append("    \\begin{subfigure}[b]{0.48\\textwidth}\n")
                            .append("        \\centering\n")
                            .append("        \\includegraphics[width=\\textwidth]{")
                            .append(slideImages.get(i + 1))
                            .append("}\n")
                            .append("    \\end{subfigure}\n")
                            .append("    \\label{fig:main}\n")
                            .append("\\end{figure}\n");
                } else {
                    slideContent.append("\\begin{figure}[htbp]\n")
                            .append("    \\centering\n")
                            .append("    \\begin{subfigure}[b]{0.48\\textwidth}\n")
                            .append("        \\centering\n")
                            .append("        \\includegraphics[width=\\textwidth]{")
                            .append(slideImages.get(i))
                            .append("}\n")
                            .append("    \\end{subfigure}\n")
                            .append("\\end{figure}\n");
                }
            }

            matcher.appendReplacement(updatedContent, Matcher.quoteReplacement(slideContent.toString()));
            slideCounter++;
        }
        matcher.appendTail(updatedContent);

        return updatedContent.toString();
    }
}
