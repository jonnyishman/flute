"""Flask CLI commands for database operations."""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

import click
import sqlalchemy as sa
from flask import current_app
from flask.cli import with_appcontext

from src.models import LearningStatus, Term, db

if TYPE_CHECKING:
    from collections.abc import Sequence

# Sample text for generating realistic book content
SAMPLE_TEXTS = [
    """The sun rose over the small village, casting long shadows across the cobblestone streets.
    Maria walked to the market, her basket swinging gently at her side. She greeted her neighbors
    with warm smiles and exchanged pleasantries about the weather. The baker had fresh bread,
    and the aroma filled the morning air. Children played in the square while their mothers
    chatted about the day's plans.""",

    """Technology has transformed the way we communicate and work. Modern smartphones contain
    more computing power than the computers that sent humans to the moon. Social media platforms
    connect billions of people across the globe, enabling instant communication and information
    sharing. However, this digital revolution also brings challenges, including privacy concerns
    and the spread of misinformation.""",

    """The ancient library stood silent in the moonlight, its weathered stone walls holding
    centuries of knowledge. Dust motes danced in the silvery beams that filtered through tall
    windows. Scrolls and books lined countless shelves, each containing stories, wisdom, and
    secrets from ages past. A single candle flickered on a wooden desk where a scholar had
    been reading late into the night.""",

    """Climate change represents one of the most pressing challenges of our time. Rising
    temperatures, melting ice caps, and changing weather patterns affect ecosystems worldwide.
    Scientists study these phenomena to better understand their causes and effects. Governments
    and organizations work to implement policies that reduce carbon emissions and promote
    sustainable practices for future generations.""",

    """The art of cooking brings families together around the dinner table. Traditional recipes
    pass from generation to generation, carrying cultural heritage and memories. Fresh ingredients,
    careful preparation, and love transform simple items into delicious meals. Each dish tells
    a story of its origins, whether from a grandmother's kitchen or a distant land's culinary
    traditions.""",
]


def generate_book_content(target_words: int) -> str:
    """Generate realistic book content with approximately target_words."""
    content_parts = []
    current_word_count = 0

    while current_word_count < target_words:
        # Select a random base text
        base_text = random.choice(SAMPLE_TEXTS)

        # Add some variation by repeating sentences or adding connectors
        variations = [
            base_text,
            f"{base_text} Meanwhile, the situation continued to develop.",
            f"As time passed, {base_text.lower()}",
            f"{base_text} This reminded everyone of similar experiences.",
            f"In those days, {base_text.lower()}",
        ]

        selected = random.choice(variations)
        content_parts.append(selected)

        # Rough word count
        current_word_count += len(selected.split())

        # Add paragraph breaks
        if len(content_parts) % 3 == 0:
            content_parts.append("\n\n")

    return " ".join(content_parts)


def create_book_via_api(title: str, language_id: int, word_count: int) -> dict:
    """Create a book using the internal API endpoint."""
    # Generate content for the book
    content = generate_book_content(word_count)

    # Split into chapters (randomly 1-5 chapters)
    num_chapters = random.randint(1, 5)
    words_per_chapter = word_count // num_chapters

    chapters: list[str] = []
    remaining_content = content

    for i in range(num_chapters):
        if i == num_chapters - 1:  # Last chapter gets remaining content
            chapters.append(remaining_content)
        else:
            # Split roughly by words
            words = remaining_content.split()
            if len(words) > words_per_chapter:
                chapter_words = words[:words_per_chapter]
                chapters.append(" ".join(chapter_words))
                remaining_content = " ".join(words[words_per_chapter:])
            else:
                chapters.append(remaining_content)
                remaining_content = ""

    # Use Flask test client to make internal API call
    with current_app.test_client() as client:
        response = client.post(
            "/api/books",
            json={
                "title": title,
                "language_id": language_id,
                "chapters": chapters,
                "source": "Generated for development",
            },
            headers={"Content-Type": "application/json"},
        )

        if response.status_code != 201:
            raise RuntimeError(f"Failed to create book: {response.get_json()}")

        return response.get_json()


def update_term_status_via_api(term_id: int, status: LearningStatus) -> None:
    """Update a term's status using the internal API endpoint."""
    with current_app.test_client() as client:
        response = client.patch(
            f"/api/terms/{term_id}",
            json={
                "status": status.value,
                "learning_stage": 1 if status == LearningStatus.LEARNING else 5,
            },
            headers={"Content-Type": "application/json"},
        )

        if response.status_code not in (200, 204):
            raise RuntimeError(f"Failed to update term {term_id}: {response.get_json()}")


def get_or_create_default_language() -> int:
    """Get or create a default language for seeding."""
    from src.models import Language

    # Try to find an existing language
    language = db.session.execute(
        sa.select(Language).limit(1)
    ).scalar_one_or_none()

    if language:
        return language.id

    # Create a default English language if none exists
    from sqlalchemy.dialects.sqlite import insert

    stmt = insert(Language).values(
        name="English",
        parser_type="spacedel",
        word_characters="a-zA-ZÀ-ÖØ-öø-ȳáéíóúÁÉÍÓÚñÑ",
    ).on_conflict_do_nothing()

    result = db.session.execute(stmt)

    if result.inserted_primary_key:
        language_id = result.inserted_primary_key[0]
    else:
        # Language was already created by another process
        language = db.session.execute(
            sa.select(Language).where(Language.name == "English")
        ).scalar_one()
        language_id = language.id

    db.session.commit()
    return language_id


@click.command("seed-db")
@click.option("--num-books", default=100, help="Number of books to create")
@click.option("--min-words", default=500, help="Minimum words per book")
@click.option("--max-words", default=2000, help="Maximum words per book")
@with_appcontext
def seed_database(num_books: int, min_words: int, max_words: int) -> None:
    """Seed the database with sample books and terms for development."""
    click.echo("🌱 Starting database seeding...")

    # Get or create default language
    language_id = get_or_create_default_language()
    click.echo(f"Using language_id: {language_id}")

    # Create books
    click.echo(f"Creating {num_books} books...")
    book_title_templates = [
        "The Adventures of Book",
        "A Tale of Wonder",
        "Journey Through Time",
        "The Mystery of Chapter",
        "Stories from the Past",
        "Modern Life Chronicles",
        "The Art of Living",
        "Scientific Discoveries",
        "Cultural Heritage",
        "Future Possibilities",
    ]

    created_books = []
    for i in range(num_books):
        title = f"{random.choice(book_title_templates)} - Volume {i+1}"
        word_count = random.randint(min_words, max_words)

        book_data = create_book_via_api(title, language_id, word_count)
        created_books.append(book_data)

        if (i + 1) % 10 == 0:
            click.echo(f"  Created {i + 1}/{num_books} books")

    click.echo(f"✅ Created {len(created_books)} books successfully")

    # Get all terms created during book creation
    click.echo("Updating term statuses...")

    terms: Sequence[Term] = db.session.execute(
        db.select(Term).where(Term.language_id == language_id)
    ).scalars().all()

    if not terms:
        click.echo("❌ No terms found to update")
        return

    click.echo(f"Found {len(terms)} terms to update")

    # Shuffle terms for random distribution
    term_list = list(terms)
    random.shuffle(term_list)

    # Calculate distribution
    total_terms = len(term_list)
    known_count = int(total_terms * 0.5)  # 50%
    learning_count = int(total_terms * 0.2)  # 20%
    # Remaining 30% stay unknown (no status update needed)

    click.echo(f"Will mark {known_count} terms as KNOWN and {learning_count} as LEARNING")

    # Update term statuses
    updated_count = 0

    # Mark first batch as KNOWN
    for term in term_list[:known_count]:
        try:
            update_term_status_via_api(term.id, LearningStatus.KNOWN)
            updated_count += 1
        except Exception as e:
            click.echo(f"  Error updating term {term.id} to KNOWN: {e}")

    # Mark second batch as LEARNING
    for term in term_list[known_count:known_count + learning_count]:
        try:
            update_term_status_via_api(term.id, LearningStatus.LEARNING)
            updated_count += 1
        except Exception as e:
            click.echo(f"  Error updating term {term.id} to LEARNING: {e}")

    click.echo(f"✅ Updated {updated_count} term statuses")
    click.echo("🎉 Database seeding completed!")
    click.echo(f"   - Created {len(created_books)} books")
    click.echo(f"   - Updated {updated_count} term statuses")
    click.echo(f"   - {known_count} terms marked as KNOWN")
    click.echo(f"   - {learning_count} terms marked as LEARNING")
    click.echo(f"   - {total_terms - known_count - learning_count} terms remain unknown")
