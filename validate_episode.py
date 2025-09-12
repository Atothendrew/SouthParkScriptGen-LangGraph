#!/usr/bin/env python3
"""
Episode YAML validation script for ensuring schema compliance.
Use this to validate new episode summaries before adding them to the database.
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import date
from typing import Dict, Any, List, Optional

def validate_basic_info(data: Dict[str, Any], file_path: str) -> List[str]:
    """Validate basic_info section."""
    errors = []
    
    if 'basic_info' not in data:
        errors.append("Missing 'basic_info' section")
        return errors
    
    basic_info = data['basic_info']
    required_fields = ['season', 'episode_number', 'title', 'original_air_date', 'episode_type']
    
    for field in required_fields:
        if field not in basic_info:
            errors.append(f"basic_info.{field} is required")
    
    # Validate data types
    if 'season' in basic_info and not isinstance(basic_info['season'], int):
        errors.append("basic_info.season must be an integer")
    
    if 'episode_number' in basic_info and not isinstance(basic_info['episode_number'], int):
        errors.append("basic_info.episode_number must be an integer")
    
    if 'title' in basic_info and not isinstance(basic_info['title'], str):
        errors.append("basic_info.title must be a string")
    
    # Validate date format
    if 'original_air_date' in basic_info:
        try:
            date.fromisoformat(basic_info['original_air_date'])
        except ValueError:
            errors.append("basic_info.original_air_date must be in YYYY-MM-DD format")
    
    # Validate episode type
    valid_types = ['standalone', 'multi_part', 'special', 'holiday']
    if 'episode_type' in basic_info and basic_info['episode_type'] not in valid_types:
        errors.append(f"basic_info.episode_type must be one of: {', '.join(valid_types)}")
    
    return errors

def validate_plot(data: Dict[str, Any]) -> List[str]:
    """Validate plot section."""
    errors = []
    
    if 'plot' not in data:
        errors.append("Missing 'plot' section")
        return errors
    
    plot = data['plot']
    required_fields = ['logline', 'plot_summary', 'plot_threads']
    
    for field in required_fields:
        if field not in plot:
            errors.append(f"plot.{field} is required")
    
    # Validate plot_threads
    if 'plot_threads' in plot:
        if not isinstance(plot['plot_threads'], list):
            errors.append("plot.plot_threads must be an array")
        elif len(plot['plot_threads']) == 0:
            errors.append("plot.plot_threads must contain at least one thread")
        else:
            for i, thread in enumerate(plot['plot_threads']):
                if not isinstance(thread, dict):
                    errors.append(f"plot.plot_threads[{i}] must be an object")
                    continue
                
                thread_fields = ['title', 'description', 'characters_involved', 'resolution_status']
                for field in thread_fields:
                    if field not in thread:
                        errors.append(f"plot.plot_threads[{i}].{field} is required")
                
                if 'resolution_status' in thread:
                    valid_statuses = ['resolved', 'unresolved', 'partially_resolved']
                    if thread['resolution_status'] not in valid_statuses:
                        errors.append(f"plot.plot_threads[{i}].resolution_status must be one of: {', '.join(valid_statuses)}")
    
    return errors

def validate_characters(data: Dict[str, Any]) -> List[str]:
    """Validate characters section."""
    errors = []
    
    if 'characters' not in data:
        errors.append("Missing 'characters' section")
        return errors
    
    characters = data['characters']
    required_sections = ['main', 'supporting', 'new']
    
    for section in required_sections:
        if section not in characters:
            errors.append(f"characters.{section} is required")
        elif not isinstance(characters[section], list):
            errors.append(f"characters.{section} must be an array")
        else:
            for i, char in enumerate(characters[section]):
                if not isinstance(char, dict):
                    errors.append(f"characters.{section}[{i}] must be an object")
                    continue
                
                # Required character fields
                char_fields = ['name', 'role', 'key_moments', 'character_development', 'relationships_affected']
                for field in char_fields:
                    if field not in char:
                        errors.append(f"characters.{section}[{i}].{field} is required")
                
                # Validate role
                if 'role' in char:
                    valid_roles = ['main', 'supporting', 'minor', 'cameo']
                    if char['role'] not in valid_roles:
                        errors.append(f"characters.{section}[{i}].role must be one of: {', '.join(valid_roles)}")
    
    return errors

def validate_content_elements(data: Dict[str, Any]) -> List[str]:
    """Validate content_elements section."""
    errors = []
    
    if 'content_elements' not in data:
        errors.append("Missing 'content_elements' section")
        return errors
    
    content = data['content_elements']
    required_sections = ['cultural_references', 'running_gags', 'locations']
    
    for section in required_sections:
        if section not in content:
            errors.append(f"content_elements.{section} is required")
        elif not isinstance(content[section], list):
            errors.append(f"content_elements.{section} must be an array")
    
    # Validate cultural references structure
    if 'cultural_references' in content:
        for i, ref in enumerate(content['cultural_references']):
            if isinstance(ref, dict):
                ref_fields = ['type', 'target', 'description', 'context']
                for field in ref_fields:
                    if field not in ref:
                        errors.append(f"content_elements.cultural_references[{i}].{field} is required")
                
                if 'type' in ref:
                    valid_types = ['celebrity', 'movie', 'tv_show', 'current_event', 'historical', 'internet_meme', 'unknown']
                    if ref['type'] not in valid_types:
                        errors.append(f"content_elements.cultural_references[{i}].type must be one of: {', '.join(valid_types[:-1])} (found: {ref['type']})")
    
    return errors

def validate_themes(data: Dict[str, Any]) -> List[str]:
    """Validate themes section."""
    errors = []
    
    if 'themes' not in data:
        errors.append("Missing 'themes' section")
        return errors
    
    themes = data['themes']
    if not isinstance(themes, list):
        errors.append("themes must be an array")
        return errors
    
    if len(themes) == 0:
        errors.append("themes must contain at least one theme")
    
    for i, theme in enumerate(themes):
        if not isinstance(theme, dict):
            errors.append(f"themes[{i}] must be an object")
            continue
        
        theme_fields = ['theme', 'description', 'how_explored']
        for field in theme_fields:
            if field not in theme:
                errors.append(f"themes[{i}].{field} is required")
    
    return errors

def validate_required_sections(data: Dict[str, Any]) -> List[str]:
    """Validate that all required top-level sections exist."""
    errors = []
    
    required_sections = ['basic_info', 'plot', 'characters', 'content_elements', 'themes', 'continuity', 'production', 'context']
    
    for section in required_sections:
        if section not in data:
            errors.append(f"Missing required section: {section}")
    
    return errors

def validate_file_format(file_path: str) -> List[str]:
    """Validate file format and naming."""
    errors = []
    
    # Check file extension
    if not file_path.endswith('.yaml'):
        errors.append("File must have .yaml extension")
    
    # Check naming convention
    filename = Path(file_path).name
    if not filename.startswith('s') or 'e' not in filename:
        errors.append("Filename should follow pattern: s{season:02d}e{episode:02d}_{title_slug}.yaml")
    
    return errors

def validate_episode_yaml(file_path: str, verbose: bool = False) -> tuple[bool, List[str]]:
    """
    Validate a single episode YAML file.
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate file format
    errors.extend(validate_file_format(file_path))
    
    # Check if file exists
    if not os.path.exists(file_path):
        errors.append(f"File not found: {file_path}")
        return False, errors
    
    # Load YAML
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML format: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"Error reading file: {e}")
        return False, errors
    
    if data is None:
        errors.append("File is empty or contains no valid YAML data")
        return False, errors
    
    # Validate sections
    errors.extend(validate_required_sections(data))
    errors.extend(validate_basic_info(data, file_path))
    errors.extend(validate_plot(data))
    errors.extend(validate_characters(data))
    errors.extend(validate_content_elements(data))
    errors.extend(validate_themes(data))
    
    is_valid = len(errors) == 0
    
    if verbose:
        if is_valid:
            print(f"✅ {file_path} - VALID")
        else:
            print(f"❌ {file_path} - INVALID")
            for error in errors:
                print(f"   - {error}")
    
    return is_valid, errors

def validate_all_episodes(episode_dir: str = "episode_summaries", verbose: bool = False) -> None:
    """Validate all episode files in the directory."""
    episode_files = list(Path(episode_dir).glob("s*.yaml"))
    
    if not episode_files:
        print(f"No episode files found in {episode_dir}")
        return
    
    print(f"Validating {len(episode_files)} episode files...")
    print("=" * 60)
    
    valid_count = 0
    total_errors = []
    
    for episode_file in sorted(episode_files):
        is_valid, errors = validate_episode_yaml(str(episode_file), verbose)
        if is_valid:
            valid_count += 1
        else:
            total_errors.extend(errors)
    
    print("=" * 60)
    print(f"✅ Valid: {valid_count}/{len(episode_files)} episodes")
    
    if total_errors:
        print(f"❌ Total errors: {len(total_errors)}")
        if not verbose:
            print("Run with --verbose flag to see detailed errors")
    else:
        print("🎉 All episodes are valid!")

def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate South Park episode YAML files")
    parser.add_argument("file", nargs="?", help="Specific file to validate (optional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed error messages")
    parser.add_argument("--all", "-a", action="store_true", help="Validate all episode files")
    
    args = parser.parse_args()
    
    if args.file:
        # Validate specific file
        is_valid, errors = validate_episode_yaml(args.file, verbose=True)
        if not is_valid:
            print(f"\n❌ Found {len(errors)} validation errors:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)
        else:
            print("\n🎉 Episode file is valid!")
    elif args.all:
        # Validate all files
        validate_all_episodes(verbose=args.verbose)
    else:
        # Default: validate all files
        validate_all_episodes(verbose=args.verbose)

if __name__ == "__main__":
    main()
