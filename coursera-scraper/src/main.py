"""Main CLI entry point for the Coursera scraper."""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .config.settings import ConfigManager
from .api.auth import CourseraAuth
from .api.coursera_client import CourseraClient
from .core.file_manager import FileManager
from .utils.exceptions import (
    CourseraScraperError, AuthenticationError, ConfigurationError
)
from .utils.logger import setup_logger

# Create console for rich output
console = Console()

@click.group()
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx):
    """
    Coursera Course Scraper - Organize course content into structured folders.
    """
    ctx.ensure_object(dict)

    # Setup basic logging
    try:
        logger = setup_logger()
        ctx.obj['logger'] = logger
    except Exception as e:
        console.print(f"[red]Failed to setup logging: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('course_name')
@click.option('--output-dir', '-o', default=None, help='Output directory for course content')
@click.option('--config-dir', '-c', default='config', help='Configuration directory')
@click.option('--dry-run', is_flag=True, help='Show what would be done without actually doing it')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def scrape(ctx, course_name, output_dir, config_dir, dry_run, verbose):
    """
    Scrape any Coursera course and organize content into folders.

    Dynamically discovers course structure for any valid Coursera course name.
    Supports all courses with lecture videos, subtitles, and transcripts.

    COURSE_NAME: Any Coursera course slug (e.g., machine-learning, business-english-intro, data-science)
    """
    logger = ctx.obj['logger']

    try:
        # Show startup banner
        console.print(Panel.fit(
            Text("Coursera Course Scraper", style="bold blue"),
            subtitle="Organizing course content..."
        ))

        if dry_run:
            console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]\n")

        # Load configuration
        console.print("[blue]Loading configuration...[/blue]")
        config = ConfigManager(config_dir)
        config.override_from_env()
        config.validate_config()

        # Override output directory if provided
        if output_dir:
            config.app_settings.default_output_dir = output_dir

        # Setup authentication
        console.print("[blue]Setting up authentication...[/blue]")
        auth = CourseraAuth()

        if not auth.is_authenticated():
            console.print("[red]Authentication failed. Please check your API token.[/red]")
            sys.exit(1)

        # Create API client
        console.print("[blue]Initializing API client...[/blue]")
        client = CourseraClient.from_config_file(
            config.config_dir / "api_endpoints.json",
            auth
        )

        # Test connection
        if not client.test_connection():
            console.print("[red]API connection test failed.[/red]")
            sys.exit(1)

        # Create file manager
        file_manager = FileManager(config.get_output_dir())

        if not dry_run:
            # Import and run scraper logic (will implement this next)
            from .core.scraper import CourseScraper

            scraper = CourseScraper(
                client=client,
                file_manager=file_manager,
                config=config,
                logger=logger
            )

            # Run the scraping
            result = scraper.scrape_course(course_name)

            if result:
                console.print(f"\n[green]SUCCESS: Successfully scraped course: {course_name}[/green]")
                console.print(f"[blue]Content saved to: {result.local_path}[/blue]")
            else:
                console.print(f"[red]Failed to scrape course: {course_name}[/red]")
                sys.exit(1)
        else:
            console.print(f"[yellow]Would scrape course: {course_name}[/yellow]")
            console.print(f"[yellow]Output directory: {config.get_output_dir()}[/yellow]")

    except AuthenticationError as e:
        console.print(f"[red]Authentication Error: {e}[/red]")
        console.print("[blue]Tip: Make sure COURSERA_API_TOKEN is set in your .env file[/blue]")
        sys.exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration Error: {e}[/red]")
        sys.exit(1)

    except CourseraScraperError as e:
        console.print(f"[red]Scraper Error: {e}[/red]")
        logger.exception("Scraper error occurred")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]Unexpected Error: {e}[/red]")
        logger.exception("Unexpected error occurred")
        sys.exit(1)


@cli.command()
@click.argument('course_name')
@click.option('--output-dir', '-o', default=None, help='Output directory for course content')
@click.option('--resolution', '-r', default='720p', help='Video resolution to download (default: 720p)')
@click.option('--max-concurrent', '-c', default=3, help='Maximum concurrent downloads (default: 3)')
@click.option('--resume', is_flag=True, help='Resume incomplete downloads')
@click.option('--subtitles/--no-subtitles', default=True, help='Download English subtitles (.vtt) (default: enabled)')
@click.option('--subtitle-language', default='en', help='Subtitle language to download (default: en)')
@click.option('--supplements/--no-supplements', default=False, help='Download supplement materials (.html) (default: disabled)')
@click.pass_context
def download(ctx, course_name, output_dir, resolution, max_concurrent, resume, subtitles, subtitle_language, supplements):
    """
    Download actual video files, subtitles, and supplements for a scraped course.

    Downloads 720p videos by default along with English subtitles (.vtt).
    Optionally downloads supplement materials (reading materials, PDFs, etc.) as HTML files.
    Files are saved with sequential naming: 1_video_name.mp4, 1_video_name.vtt, 1_supplement_name.html

    COURSE_NAME: The course that was already scraped
    """
    logger = ctx.obj['logger']

    try:
        # Show startup banner
        subtitle_info = f" + {subtitle_language.upper()} subtitles" if subtitles else ""
        supplement_info = " + supplements" if supplements else ""
        console.print(Panel.fit(
            Text("Coursera Content Downloader", style="bold green"),
            subtitle=f"Downloading {resolution} videos{subtitle_info}{supplement_info}..."
        ))

        # Load configuration
        console.print("[blue]Loading configuration...[/blue]")
        config = ConfigManager()

        # Override output directory if provided
        if output_dir:
            config.app_settings.default_output_dir = output_dir

        # Setup authentication
        console.print("[blue]Setting up authentication...[/blue]")
        auth = CourseraAuth()

        if not auth.is_authenticated():
            console.print("[red]Authentication failed. Please check your API token.[/red]")
            sys.exit(1)

        # Create file manager
        file_manager = FileManager(config.get_output_dir())

        # Check if course exists
        course_path = file_manager.get_existing_course_path(course_name)
        if not course_path:
            console.print(f"[red]Course not found: {course_name}[/red]")
            console.print("[blue]Run 'scrape' command first to extract course structure[/blue]")
            sys.exit(1)

        console.print(f"[green]Found course: {course_path}[/green]")

        # Load course metadata
        metadata_file = course_path / "course_metadata.json"
        if not metadata_file.exists():
            console.print("[red]Course metadata not found. Run 'scrape' command first.[/red]")
            sys.exit(1)

        # Import and run downloader
        from .api.enhanced_downloader import EnhancedVideoDownloader

        downloader = EnhancedVideoDownloader(
            auth=auth,
            file_manager=file_manager,
            max_concurrent=max_concurrent,
            download_subtitles=subtitles,
            subtitle_language=subtitle_language,
            download_supplements=supplements,
            logger=logger
        )

        # Start downloading
        result = downloader.download_course_videos_and_subtitles(
            course_path=course_path,
            target_resolution=resolution,
            resume=resume
        )

        if result:
            video_stats = result.get('videos', {})
            subtitle_stats = result.get('subtitles', {})
            supplement_stats = result.get('supplements', {})

            console.print(f"\n[green]SUCCESS: Downloaded content[/green]")
            console.print(f"[blue]Videos: {video_stats.get('downloaded', 0)} downloaded | {video_stats.get('skipped', 0)} skipped | {video_stats.get('failed', 0)} failed[/blue]")
            console.print(f"[blue]Subtitles: {subtitle_stats.get('downloaded', 0)} downloaded | {subtitle_stats.get('skipped', 0)} skipped | {subtitle_stats.get('failed', 0)} failed[/blue]")
            console.print(f"[blue]Supplements: {supplement_stats.get('downloaded', 0)} downloaded | {supplement_stats.get('skipped', 0)} skipped | {supplement_stats.get('failed', 0)} failed[/blue]")
        else:
            console.print("[red]Download failed[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Download Error: {e}[/red]")
        logger.exception("Download error occurred")
        sys.exit(1)


@cli.command()
@click.option('--config-dir', '-c', default='config', help='Configuration directory')
def config(config_dir):
    """Show current configuration."""
    try:
        config_mgr = ConfigManager(config_dir)

        # Create table for settings
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="magenta")

        # App settings
        if config_mgr.app_settings:
            settings = config_mgr.app_settings
            table.add_row("Output Directory", settings.default_output_dir)
            table.add_row("Log Level", settings.log_level)
            table.add_row("Max Filename Length", str(settings.max_filename_length))
            table.add_row("Max Concurrent Requests", str(settings.max_concurrent_requests))
            table.add_row("Request Timeout", f"{settings.request_timeout}s")
            table.add_row("Retry Attempts", str(settings.retry_attempts))

        # Download settings
        if config_mgr.download_settings:
            download = config_mgr.download_settings
            table.add_row("", "")  # Separator
            table.add_row("Download Files", str(download.download_files))
            table.add_row("File Types", ", ".join(download.file_types))
            table.add_row("Max File Size", f"{download.max_file_size_mb}MB")
            table.add_row("Concurrent Downloads", str(download.concurrent_downloads))
            table.add_row("Skip Existing", str(download.skip_existing))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
def test():
    """Test API connection and authentication."""
    try:
        console.print("[blue]Testing authentication and API connection...[/blue]")

        # Test authentication
        try:
            auth = CourseraAuth()
            console.print("[green]SUCCESS: Authentication token loaded[/green]")
        except AuthenticationError as e:
            console.print(f"[red]ERROR: Authentication failed: {e}[/red]")
            return

        # Test configuration
        try:
            config = ConfigManager()
            console.print("[green]SUCCESS: Configuration loaded[/green]")
        except ConfigurationError as e:
            console.print(f"[red]ERROR: Configuration failed: {e}[/red]")
            return

        # Test API client
        try:
            client = CourseraClient.from_config_file("config/api_endpoints.json", auth)
            console.print("[green]SUCCESS: API client initialized[/green]")
        except Exception as e:
            console.print(f"[red]ERROR: API client failed: {e}[/red]")
            return

        # Test connection
        if client.test_connection():
            console.print("[green]SUCCESS: API connection successful[/green]")
        else:
            console.print("[red]ERROR: API connection failed[/red]")
            return

        console.print("\n[green]All tests passed! Ready to scrape courses.[/green]")

    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")


@cli.command()
@click.option('--course-dir', help='Specific course directory to check')
def status(course_dir):
    """Show status of scraped courses."""
    try:
        import json
        config = ConfigManager()
        file_manager = FileManager(config.get_output_dir())

        base_dir = file_manager.base_output_dir

        if not base_dir.exists():
            console.print(f"[yellow]No courses found in: {base_dir}[/yellow]")
            return

        # If specific course requested, show detailed status
        if course_dir:
            course_path = base_dir / course_dir
            if not course_path.exists():
                console.print(f"[red]Course not found: {course_path}[/red]")
                return

            # Show detailed course information
            console.print(f"\n[bold cyan]Course: {course_dir}[/bold cyan]")
            console.print(f"[blue]Location: {course_path}[/blue]\n")

            # Count modules and lessons
            module_count = 0
            total_lessons = 0
            total_videos = 0
            total_size_mb = 0

            for module_path in sorted(course_path.glob("module-*")):
                if module_path.is_dir():
                    module_count += 1
                    lesson_dirs = [d for d in module_path.glob("lesson-*") if d.is_dir()]
                    total_lessons += len(lesson_dirs)

                    # Count videos in this module
                    for lesson_dir in lesson_dirs:
                        video_files = list(lesson_dir.glob("*.mp4")) + list(lesson_dir.glob("*.webm"))
                        total_videos += len(video_files)
                        for vf in video_files:
                            total_size_mb += vf.stat().st_size / 1024 / 1024

            # Create detailed table
            table = Table(title=f"Course Details: {course_dir}")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta", justify="right")

            table.add_row("Total Modules", str(module_count))
            table.add_row("Total Lessons", str(total_lessons))
            table.add_row("Total Videos", str(total_videos))
            table.add_row("Total Size", f"{total_size_mb:.1f} MB ({total_size_mb/1024:.2f} GB)")

            # Check progress
            progress_path = file_manager.get_progress_file_path(course_path)
            if progress_path.exists():
                try:
                    with open(progress_path, 'r') as f:
                        progress = json.load(f)
                    status_text = "Complete" if progress.get('is_complete', False) else "In Progress"
                    last_updated = progress.get('last_update', 'Unknown')
                    table.add_row("Status", status_text)
                    table.add_row("Last Updated", last_updated)
                except:
                    table.add_row("Status", "Unknown")
            else:
                table.add_row("Status", "No progress data")

            console.print(table)

            # Show module breakdown
            console.print("\n[bold cyan]Module Breakdown:[/bold cyan]")
            for module_path in sorted(course_path.glob("module-*")):
                if module_path.is_dir():
                    lesson_dirs = [d for d in module_path.glob("lesson-*") if d.is_dir()]
                    videos_in_module = sum(len(list(ld.glob("*.mp4"))) for ld in lesson_dirs)
                    console.print(f"  [blue]{module_path.name}[/blue]: {len(lesson_dirs)} lessons, {videos_in_module} videos")

        else:
            # Show all courses
            table = Table(title="All Courses")
            table.add_column("Course", style="cyan")
            table.add_column("Modules", justify="center")
            table.add_column("Lessons", justify="center")
            table.add_column("Videos", justify="center")
            table.add_column("Status", style="green")

            course_count = 0
            for course_path in base_dir.iterdir():
                if course_path.is_dir() and not course_path.name.startswith('.'):
                    course_count += 1

                    # Count modules and lessons
                    module_count = len([p for p in course_path.glob("module-*") if p.is_dir()])
                    lesson_count = len(list(course_path.rglob("lesson-*")))
                    video_count = len(list(course_path.glob("**/*.mp4")))

                    # Check for progress file
                    progress_path = file_manager.get_progress_file_path(course_path)
                    if progress_path.exists():
                        try:
                            with open(progress_path, 'r') as f:
                                progress = json.load(f)
                            status = "Complete" if progress.get('is_complete', False) else "In Progress"
                        except:
                            status = "Unknown"
                    else:
                        status = "Unknown"

                    table.add_row(
                        course_path.name,
                        str(module_count),
                        str(lesson_count),
                        str(video_count),
                        status
                    )

            if course_count == 0:
                console.print("[yellow]No courses found.[/yellow]")
            else:
                console.print(table)
                console.print(f"\n[blue]Total courses: {course_count}[/blue]")

    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")


if __name__ == '__main__':
    cli()