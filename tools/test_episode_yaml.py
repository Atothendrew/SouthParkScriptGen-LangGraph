#!/usr/bin/env python3
"""Test script for episode YAML loading functionality."""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spgen.schemas import EpisodeSummaryLoader, EpisodeDatabase

def test_yaml_loading():
    """Test loading the S01E01 episode from YAML."""
    print("Testing YAML episode loading...")
    
    # Test loading from YAML file
    try:
        episode = EpisodeSummaryLoader.load_from_yaml("episode_summaries/s01e01_cartman_gets_an_anal_probe.yaml")
        
        print(f"✅ Successfully loaded episode: S{episode.season:02d}E{episode.episode_number:02d} - {episode.title}")
        print(f"   Air Date: {episode.original_air_date}")
        print(f"   Episode Type: {episode.episode_type.value}")
        print(f"   Logline: {episode.logline}")
        
        # Test character data
        print(f"\n📺 Main Characters ({len(episode.main_characters)}):")
        for char in episode.main_characters:
            print(f"   - {char.name} ({char.role.value})")
        
        # Test plot threads
        print(f"\n📖 Plot Threads ({len(episode.plot_threads)}):")
        for thread in episode.plot_threads:
            print(f"   - {thread.title}: {thread.resolution_status}")
        
        # Test cultural references
        print(f"\n🎭 Cultural References ({len(episode.cultural_references)}):")
        for ref in episode.cultural_references:
            print(f"   - {ref.target} ({ref.reference_type})")
        
        # Test running gags
        print(f"\n😂 Running Gags ({len(episode.running_gags)}):")
        for gag in episode.running_gags:
            print(f"   - {gag.gag_name} (frequency: {gag.frequency_in_episode})")
        
        # Test themes
        print(f"\n🎯 Themes ({len(episode.themes)}):")
        for theme in episode.themes:
            print(f"   - {theme.theme}")
        
        print("\n✅ All episode data loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading episode: {e}")
        return False
    
    return True

def test_episode_database():
    """Test the episode database functionality."""
    print("\n" + "="*50)
    print("Testing Episode Database...")
    
    try:
        # Initialize database
        db = EpisodeDatabase("episode_summaries")
        
        print(f"✅ Database initialized with {len(db)} episodes")
        
        # Test getting episode by season/episode
        episode = db.get_episode(1, 1)
        if episode:
            print(f"✅ Retrieved S01E01: {episode.title}")
        else:
            print("❌ Could not retrieve S01E01")
            return False
        
        # Test getting episode by ID
        episode = db.get_episode_by_id("S01E01")
        if episode:
            print(f"✅ Retrieved by ID S01E01: {episode.title}")
        else:
            print("❌ Could not retrieve by ID S01E01")
            return False
        
        # Test search functionality
        search_results = db.search_episodes("alien")
        print(f"✅ Search for 'alien' found {len(search_results)} episodes")
        
        # Test character appearances
        cartman_episodes = db.get_character_appearances("Cartman")
        print(f"✅ Cartman appears in {len(cartman_episodes)} episodes")
        
        # Test running gag episodes
        kenny_death_episodes = db.get_running_gag_episodes("Kenny Dies")
        print(f"✅ 'Kenny Dies' gag appears in {len(kenny_death_episodes)} episodes")
        
        print("\n✅ All database functionality working!")
        
    except Exception as e:
        print(f"❌ Error with database: {e}")
        return False
    
    return True

def test_yaml_serialization():
    """Test converting back to YAML."""
    print("\n" + "="*50)
    print("Testing YAML Serialization...")
    
    try:
        # Load episode
        episode = EpisodeSummaryLoader.load_from_yaml("episode_summaries/s01e01_cartman_gets_an_anal_probe.yaml")
        
        # Save to a new file
        test_file = "test_episode_output.yaml"
        EpisodeSummaryLoader.save_to_yaml(episode, test_file)
        
        # Load it back
        reloaded_episode = EpisodeSummaryLoader.load_from_yaml(test_file)
        
        # Compare key fields
        if (episode.title == reloaded_episode.title and 
            episode.season == reloaded_episode.season and
            episode.episode_number == reloaded_episode.episode_number and
            len(episode.main_characters) == len(reloaded_episode.main_characters)):
            print("✅ YAML serialization round-trip successful!")
            
            # Clean up test file
            import os
            os.remove(test_file)
            
            return True
        else:
            print("❌ YAML serialization round-trip failed - data mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Error with YAML serialization: {e}")
        return False

if __name__ == "__main__":
    print("🎬 South Park Episode YAML Loading Test")
    print("="*50)
    
    success = True
    
    # Run tests
    success &= test_yaml_loading()
    success &= test_episode_database()
    success &= test_yaml_serialization()
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! YAML episode loading is working correctly.")
    else:
        print("💥 Some tests failed. Check the output above for details.")
    
    print("="*50)
