import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import matplotlib.pyplot as plt
from collections import Counter
import arabic_reshaper
from bidi.algorithm import get_display
import logging


class CleaningPipeline:
    def __init__(self, input_file, output_dir, api_key=None, save_intermediate=True):
        self.input_file = input_file
        self.output_dir = output_dir
        self.api_key = api_key
        self.save_intermediate = save_intermediate
        
        # Create output directory first
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Then setup logging
        self.logger = self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s — %(levelname)s — %(message)s',
            handlers=[
                logging.FileHandler(f"{self.output_dir}/app.log", encoding='utf-8'),
                logging.StreamHandler()  # Also logs to console
            ]
        )
        return logging.getLogger()

    def read_json_file(self, file_path):
        """Read JSON file and return its contents."""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def write_json_file(self, data, file_path):
        """Write data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def fix_ids(self, questions):
        """Fix IDs by assigning new sequential IDs."""
        for new_id, entry in enumerate(questions):
            entry['id'] = new_id + 1  # Start IDs from 1
        return questions

    def find_similar_questions(self, questions_with_ids, threshold=0.8):
        """Find similar questions based on cosine similarity of their TF-IDF vectors."""
        questions = [entry['question'] for entry in questions_with_ids]
        ids = [entry['id'] for entry in questions_with_ids]

        # Vectorize with TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(questions)

        # Cosine similarity
        cos_sim_matrix = cosine_similarity(tfidf_matrix)

        # Find similar pairs
        similar_pairs = {}
        seen_pairs = set()

        for i in range(len(cos_sim_matrix)):
            for j in range(i + 1, len(cos_sim_matrix)):
                if cos_sim_matrix[i][j] > threshold:
                    pair = tuple(sorted([ids[i], ids[j]]))
                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        for a, b in [(ids[i], ids[j]), (ids[j], ids[i])]:
                            if a not in similar_pairs:
                                similar_pairs[a] = []
                            similar_pairs[a].append(b)

        # Group duplicates
        visited = set()
        duplicate_groups = []

        def collect_group(start_id):
            group = set([start_id])
            stack = [start_id]
            while stack:
                current_id = stack.pop()
                for neighbor in similar_pairs.get(current_id, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        group.add(neighbor)
                        stack.append(neighbor)
            return sorted(group)

        for question_id in similar_pairs.keys():
            if question_id not in visited:
                visited.add(question_id)
                group = collect_group(question_id)
                duplicate_groups.append(group)

        # Get unique_ids
        duplicate_ids = set(id for group in duplicate_groups for id in group)
        unique_ids = []

        # Add one representative from each duplicate group
        for group in duplicate_groups:
            unique_ids.append(group[0])

        # Add non-duplicate ids
        for id in ids:
            if id not in duplicate_ids:
                unique_ids.append(id)

        return sorted(unique_ids)

    def filter_questions_by_ids(self, questions_with_ids, unique_ids):
        """Filter questions to keep only those with unique IDs."""
        return [
            entry
            for entry in questions_with_ids
            if entry["id"] in unique_ids
        ]

    def clean_with_gpt(self, data):
        """Clean questions using GPT to remove non-Arabic words and fix formatting."""
        if not self.api_key:
            return data

        client = OpenAI(api_key=self.api_key)
        cleaned = []
        
        def build_prompt(q):
            return f"""
              1. Remove any trailing sentence like 'وفق قانون العمل المصري' or 'وفق المادة 131 من قانون العمل المصري', but keep the question
              2. Remove any question that contains non-Arabic **letters** (but keep numbers).
              3. don't give any conclusion or introduction

              ### Question:
              {q}
              """
        
        for item in data:
            prompt = build_prompt(item['question'])
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=[
                    {"role": "system", "content": "أنت مساعد ذكي مختص في تنقيح الأسئلة القانونية."},
                    {"role": "user", "content": prompt}
                ]
            )
            output = response.choices[0].message.content
            if output:
                cleaned.append({'id': item['id'], 'question': output})
        return cleaned

    def remove_invalid_entries(self, data):
        """Remove entries that don't match the expected structure."""
        expected_structure = {
            "id": int,
            "question": str,
            "ground_truth": str,
            "reasoning_required": list,
            "quality_control": {
                "reasoning_path": {
                    "steps": list
                },
                "citation_reference": {
                    "primary_citations": list,
                    "supporting_citations": list,
                    "cross_references": list,
                    "relevance_mapping": dict
                }
            },
            "difficulty_level": {
                "level": str,
                "factors": list
            },
            "question_type": str,
            "retrieval_testing": {
                "type": str,
                "retrieval_pattern": str,
                "variations": {
                    "keywords": list,
                    "concepts": list
                }
            },
            "metadata": {
                "topic": str,
                "subtopic": str,
                "language_level": str
            }
        }

        def validate_entry(entry, structure, entry_index):
            if not isinstance(entry, dict):
                return f"Entry {entry_index} is not a valid dictionary."
            for key, value in structure.items():
                if key not in entry:
                    return f"Entry {entry_index}: Missing key: {key}"
                if isinstance(value, dict):
                    sub_result = validate_entry(entry[key], value, entry_index)
                    if sub_result:
                        return sub_result
                elif not isinstance(entry[key], value):
                    return f"Entry {entry_index}: Incorrect type for key: {key}. Expected {value}, got {type(entry[key])}"
            return None

        valid_entries = []
        invalid_count = 0

        for index, entry in enumerate(data):
            validation_result = validate_entry(entry, expected_structure, index + 1)
            if not validation_result:
                valid_entries.append(entry)
            else:
                invalid_count += 1
                print(validation_result)
                self.logger.info(validation_result)

        print(f"Total invalid entries: {invalid_count}")
        self.logger.info(f"Total invalid entries: {invalid_count}")
        return valid_entries

    def visualize_all_fields(self, json_path, show_visualizations=False):
        """Generate visualizations for the data."""
        os.makedirs(self.output_dir, exist_ok=True)
        data = self.read_json_file(json_path)

        # Extract fields
        difficulty_levels = []
        question_types = []
        primary_citations = []
        reasoning_required = []
        retrieval_testing_types = []
        topics = []
        subtopics = []

        for entry in data:
            difficulty_levels.append(entry.get('difficulty_level', {}).get('level', None))
            question_types.append(entry.get('question_type', None))
            primary_citations.append(entry.get('quality_control', {}).get('citation_reference', {}).get('primary_citations', []))
            reasoning_required.append(entry.get('reasoning_required', []))
            retrieval_testing_types.append(entry.get('retrieval_testing', {}).get('type', None))
            topics.append(entry.get('metadata', {}).get('topic', None))
            subtopics.append(entry.get('metadata', {}).get('subtopic', None))

        # Clean data
        difficulty_levels = [x for x in difficulty_levels if x is not None]
        question_types = [x for x in question_types if x is not None]
        retrieval_testing_types = [x for x in retrieval_testing_types if x is not None]
        flat_reasoning_required = [item for sublist in reasoning_required for item in sublist]
        flat_primary_citations = [item for sublist in primary_citations for item in sublist]

        def save_plot(plot_func, filename):
            plot_func()
            plt.savefig(filename)
            if show_visualizations:
                plt.show()
            plt.close()

        # Plot grid for other fields
        def plot_grid():
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))

            # Difficulty Levels
            axes[0, 0].bar(*zip(*Counter(difficulty_levels).items()))
            axes[0, 0].set_title('Distribution of Difficulty Levels')
            axes[0, 0].set_ylabel('Count')
            axes[0, 0].set_xlabel('Difficulty Level')
            axes[0, 0].tick_params(axis='x', rotation=45)

            # Question Types
            axes[0, 1].bar(*zip(*Counter(question_types).items()))
            axes[0, 1].set_title('Distribution of Question Types')
            axes[0, 1].set_ylabel('Count')
            axes[0, 1].set_xlabel('Question Type')
            axes[0, 1].tick_params(axis='x', rotation=45)

            # Reasoning Required
            axes[1, 0].bar(*zip(*Counter(flat_reasoning_required).items()))
            axes[1, 0].set_title('Distribution of Reasoning Required')
            axes[1, 0].set_ylabel('Count')
            axes[1, 0].set_xlabel('Reasoning Type')
            axes[1, 0].tick_params(axis='x', rotation=45)

            # Retrieval Testing Types
            axes[1, 1].bar(*zip(*Counter(retrieval_testing_types).items()))
            axes[1, 1].set_title('Distribution of Retrieval Testing Types')
            axes[1, 1].set_ylabel('Count')
            axes[1, 1].set_xlabel('Retrieval Testing Type')
            axes[1, 1].tick_params(axis='x', rotation=45)

            plt.tight_layout()
        save_plot(plot_grid, f"{self.output_dir}/other_fields_grid.png")

    def run(self):
        """
        Run the complete cleaning pipeline.
        
        Returns:
            dict: Final cleaned data
        """
        print("\n=== Starting Cleaning Pipeline ===")
        self.logger.info("\n=== Starting Cleaning Pipeline ===")
        print(f"Input file: {self.input_file}")
        self.logger.info(f"Input file: {self.input_file}")
        print(f"Output directory: {self.output_dir}")
        self.logger.info(f"Output directory: {self.output_dir}")
        
        # Step 1: Read input file
        data = self.read_json_file(self.input_file)
        initial_count = len(data)
        print(f"\nStep 1: Reading input file")
        self.logger.info(f"\nStep 1: Reading input file")
        print(f"Initial number of entries: {initial_count}")
        self.logger.info(f"Initial number of entries: {initial_count}")
        
        # Step 2: Fix IDs
        print("\nStep 2: Fixing IDs")
        self.logger.info("\nStep 2: Fixing IDs")
        data_with_fixed_ids = self.fix_ids(data)
        if self.save_intermediate:
            self.write_json_file(data_with_fixed_ids, f"{self.output_dir}/gen_questions_ids.json")
            print(f"Saved fixed IDs to: {self.output_dir}/gen_questions_ids.json")
            self.logger.info(f"Saved fixed IDs to: {self.output_dir}/gen_questions_ids.json")

        # Step 3: Remove duplicates
        print("\nStep 3: Removing duplicates")
        self.logger.info("\nStep 3: Removing duplicates")
        questions_with_ids = [
            {"id": entry["id"], "question": entry["question"]["question"] if isinstance(entry["question"], dict) else entry["question"]}
            for entry in data_with_fixed_ids
        ]
        unique_ids = self.find_similar_questions(questions_with_ids)
        unique_questions = self.filter_questions_by_ids(data_with_fixed_ids, unique_ids)
        duplicates_removed = len(data_with_fixed_ids) - len(unique_questions)
        print(f"Removed {duplicates_removed} duplicate entries")
        self.logger.info(f"Removed {duplicates_removed} duplicate entries")
        print(f"Remaining unique entries: {len(unique_questions)}")
        self.logger.info(f"Remaining unique entries: {len(unique_questions)}")
        
        if self.save_intermediate:
            self.write_json_file(unique_questions, f"{self.output_dir}/unique_gen_questions.json")
            print(f"Saved unique questions to: {self.output_dir}/unique_gen_questions.json")
            self.logger.info(f"Saved unique questions to: {self.output_dir}/unique_gen_questions.json")
        
        # Step 4: Clean with GPT
        if self.api_key:
            print("\nStep 4: Cleaning with GPT")
            self.logger.info("\nStep 4: Cleaning with GPT")
            questions_for_cleaning = [
                {"id": entry["id"], "question": entry["question"]["question"] if isinstance(entry["question"], dict) else entry["question"]}
                for entry in unique_questions
            ]
            cleaned_data = self.clean_with_gpt(questions_for_cleaning)
            
            # Update questions with cleaned versions
            for entry in unique_questions:
                cleaned_entry = next((item for item in cleaned_data if item["id"] == entry["id"]), None)
                if cleaned_entry:
                    entry["question"] = cleaned_entry["question"]
            
            if self.save_intermediate:
                self.write_json_file(unique_questions, f"{self.output_dir}/gen_unique_QA.json")
                print(f"Saved GPT-cleaned questions to: {self.output_dir}/gen_unique_QA.json")
                self.logger.info(f"Saved GPT-cleaned questions to: {self.output_dir}/gen_unique_QA.json")
        
        # Step 5: Remove invalid entries
        print("\nStep 5: Removing invalid entries")
        self.logger.info("\nStep 5: Removing invalid entries")
        valid_entries = self.remove_invalid_entries(unique_questions)
        invalid_removed = len(unique_questions) - len(valid_entries)
        print(f"Removed {invalid_removed} invalid entries")
        self.logger.info(f"Removed {invalid_removed} invalid entries")
        print(f"Remaining valid entries: {len(valid_entries)}")
        self.logger.info(f"Remaining valid entries: {len(valid_entries)}")
        
        if self.save_intermediate:
            self.write_json_file(valid_entries, f"{self.output_dir}/valid_entries.json")
            print(f"Saved valid entries to: {self.output_dir}/valid_entries.json")
            self.logger.info(f"Saved valid entries to: {self.output_dir}/valid_entries.json")

        # Step 6: Generate visualizations and analyze citations
        print("\nStep 6: Generating visualizations and analyzing citations")
        self.logger.info("\nStep 6: Generating visualizations and analyzing citations")
        self.visualize_all_fields(f"{self.output_dir}/valid_entries.json")
        print(f"Generated visualizations in: {self.output_dir}/visualizations")
        self.logger.info(f"Generated visualizations in: {self.output_dir}/visualizations")
        
        # Analyze citations
        all_citations = []
        for entry in valid_entries:
            citations = entry.get('quality_control', {}).get('citation_reference', {}).get('primary_citations', [])
            all_citations.extend(citations)
        
        citation_counts = Counter(all_citations)
        max_citation = max([int(c) for c in citation_counts.keys() if c.isdigit()], default=0)
        full_range = list(range(1, max_citation + 1))
        unmentioned = [i for i in full_range if str(i) not in citation_counts]
        
        print("\nCitation Analysis:")
        self.logger.info("\nCitation Analysis:")
        print(f"Total unique citations used: {len(citation_counts)}")
        self.logger.info(f"Total unique citations used: {len(citation_counts)}")
        print(f"Highest citation number: {max_citation}")
        self.logger.info(f"Highest citation number: {max_citation}")
        print(f"Number of unmentioned citations: {len(unmentioned)}")
        self.logger.info(f"Number of unmentioned citations: {len(unmentioned)}")
        print("Unmentioned citation IDs:", unmentioned[:20], "..." if len(unmentioned) > 20 else "")
        self.logger.info("Unmentioned citation IDs:", unmentioned[:20], "..." if len(unmentioned) > 20 else "")
        
        # Save unmentioned citations to a file
        with open(f"{self.output_dir}/unmentioned_citations.txt", "w", encoding="utf-8") as file:
            file.write("Unmentioned Citation IDs:\n")
            file.write("\n".join(map(str, unmentioned)))
        print(f"Saved unmentioned citations to: {self.output_dir}/unmentioned_citations.txt")
        self.logger.info(f"Saved unmentioned citations to: {self.output_dir}/unmentioned_citations.txt")

        # Final statistics
        print("\n=== Final Statistics ===")
        self.logger.info("\n=== Final Statistics ===")
        print(f"Initial entries: {initial_count}")
        self.logger.info(f"Initial entries: {initial_count}")
        print(f"After removing duplicates: {len(unique_questions)}")
        self.logger.info(f"After removing duplicates: {len(unique_questions)}")
        print(f"After removing invalid entries: {len(valid_entries)}")
        self.logger.info(f"After removing invalid entries: {len(valid_entries)}")
        print(f"Total entries removed: {initial_count - len(valid_entries)}")
        self.logger.info(f"Total entries removed: {initial_count - len(valid_entries)}")
        print(f"Final dataset contains {len(valid_entries)} entries")
        self.logger.info(f"Final dataset contains {len(valid_entries)} entries")
        
        return valid_entries


if __name__ == "__main__":
    # Example usage
    input_file = "questions6.json"
    output_dir = "cleaned_output"
    api_key = os.getenv("OPENAI_API_KEY")  # Get API key from environment variable
    
    pipeline = CleaningPipeline(input_file, output_dir, api_key)
    cleaned_data = pipeline.run()
    print(f"\nCleaning complete. Final dataset contains {len(cleaned_data)} entries.")
    pipeline.logger.info(f"\nCleaning complete. Final dataset contains {len(cleaned_data)} entries.") 