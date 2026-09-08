#import DaVinciResolveScript as dvr_script
from json import tool
import pprint
from time import sleep  

#resolve exists in the global namespace, so we can use it directly, only can runs from daVinci Resolve's scripting console
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
mediaPool = project.GetMediaPool()
timeline = project.GetCurrentTimeline()

def prepareTimeline():
    global timeline
    if not timeline:
        print("No active timeline found, creating a new one.")
        timeline = mediaPool.CreateEmptyTimeline("New Timeline")
        project.SetCurrentTimeline(timeline)

    video_track_count = timeline.GetTrackCount("video")
    audio_track_count = timeline.GetTrackCount("audio")
    print(f"{timeline.GetName()} has {video_track_count} video tracks and {audio_track_count} audio tracks.")

    # create video1 video2 and title track if they do not exist
    if video_track_count < 3:
        for i in range(1,4):
            if i <= video_track_count :
                print(f"Video {i}. '{timeline.GetTrackName('video', i)}' already exists.")
            else:
                if timeline.AddTrack("video"):
                    print(f"Video {i} added.")

            timeline.SetTrackName("video", i, f"Video {i}")
    else:
        print("Timeline already has 3 or more video tracks.")
    
    if audio_track_count < 2:
        for i in range(1,3):
            if i <= audio_track_count :
                print(f"Audio {i}. '{timeline.GetTrackName('audio', i)}' already exists.")
            else:
                if timeline.AddTrack("audio"):
                    print(f"Audio {i} added.")

            timeline.SetTrackName("audio", i, f"Audio {i}")
    else:
        print("Timeline already has 2 or more audio tracks.")

def add_filenames_to_timeline():
    if not timeline:
        print("no active timeline.")
        return

    clipList = mediaPool.GetRootFolder().GetClipList()
    print(f"Found {len(clipList)} clips in current folder.")

    clipList = sorted(clipList, key = lambda clip : clip.GetClipProperty("File Name"))

    trackIndex = 0
    for clip in clipList[:]:
        trackIndex = 1 #trackIndex%2 + 1
        #print(clip)
        name = clip.GetName()
        
        timeline.SetTrackLock("video", 1, True)
        timeline.SetTrackLock("video", 2, True)

        clip_info = [{
            'mediaPoolItem': clip,
            'trackIndex': 3,
            'mediaType': 1,
        }]
        
        newTimelineItem = mediaPool.AppendToTimeline(clip_info)
        sleep(.1)
        if not newTimelineItem:
            print(f"Could not add clip {name} to timeline.")
            continue
        
        newTimelineItem = newTimelineItem[0]
        #print(newTimelineItem)
        duration = newTimelineItem.GetDuration()

        start_frame = newTimelineItem.GetStart()
        title = name[name.find(" ")+1:name.rfind("[")-1]
        print(f"{start_frame} +{duration} '{title}'")

        timeline.SetCurrentTimecode(str(start_frame))
        sleep(.1)
        new_text_clip = timeline.InsertFusionTitleIntoTimeline("Text+")
        #pprint.pprint(new_text_clip)
        if new_text_clip:
            #print(f"{new_text_clip.GetProperty('trackIndex')} added to timeline.")
            new_text_clip.trackIndex = 3
            new_text_clip.SetProperty("trackIndex", 3)
            new_text_clip.SetProperty("text", title)

            # Fusion paraméterek módosítása
            comp = new_text_clip.GetFusionCompByIndex(1)
            sleep(.1)
            if comp:
                tool = comp.FindTool("Template")
                
                if tool:
                    tool.SetInput("StyledText", title.capitalize(), 0)
                    tool.SetInput("Font", "LG Display-Regular", 0)
                    tool.SetInput("Style", "Regular", 0)
                    tool.SetInput("Size", 0.07, 0) 
                    tool.SetInput("Center", {1: 0.5, 2: 0.9}, 0)
                    tool.SetInput("VJustify", 1, 0)

                    tool.SetInput("Red1", 1.0, 0)
                    tool.SetInput("Green1", 0.4, 0)
                    tool.SetInput("Blue1", 0.7, 0)

                    tool.SetInput("Enabled2", 1, 0) 
                    
                    tool.SetInput("Red2", 0.0, 0)
                    tool.SetInput("Green2", 0.0, 0)
                    tool.SetInput("Blue2", 0.0, 0)
                    
                    tool.SetInput("Thickness2", 0.1, 0)
                    tool.SetInput("Softness2X", 0.05, 0)
                    tool.SetInput("Softness2Y", 0.05, 0)

        clip_info_final = [{
            'mediaPoolItem': clip,
            'trackIndex': trackIndex,
        }]

        timeline.DeleteClips([newTimelineItem])
        sleep(.2)
        timeline.SetTrackLock("video", 1, False)
        timeline.SetTrackLock("video", 2, False)
        timeline.SetCurrentTimecode(str(start_frame))
        newTimelineItem2 = mediaPool.AppendToTimeline(clip_info_final)
        if not newTimelineItem2:
            print(f"Could not add clip {name} to timeline.")
            continue
    
        sleep(.1)
    print("Kész! A feliratok a helyükre kerültek.")

if __name__ == "__main__":
    print("Title.py running from DaVinci Resolve scripting console.")
    
    prepareTimeline()
    add_filenames_to_timeline()