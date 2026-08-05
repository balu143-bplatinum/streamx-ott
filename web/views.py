# web/views.py
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Video, Advertisement, WatchProgress


def index(request):
    """Initial page load displaying catalog, continue watching, and watchlist."""
    watched_ids = request.session.get('continue_watching', [])
    watchlist_ids = request.session.get('watchlist', [])
    
    continue_watching_videos = []
    if watched_ids:
        videos_dict = Video.objects.in_bulk(watched_ids)
        continue_watching_videos = [videos_dict[vid] for vid in watched_ids if vid in videos_dict]

    watchlist_videos = []
    if watchlist_ids:
        videos_dict = Video.objects.in_bulk(watchlist_ids)
        watchlist_videos = [videos_dict[vid] for vid in watchlist_ids if vid in watchlist_ids]

    videos = Video.objects.all().order_by('-created_at')
    categories = Video.objects.values_list('category', flat=True).distinct()

    return render(request, 'web/index.html', {
        'videos': videos,
        'continue_watching_videos': continue_watching_videos,
        'watchlist_videos': watchlist_videos,
        'categories': categories,
    })


def video_detail(request, pk):
    """Detail view for streaming video + mid-roll ad cue points + watch history."""
    video = get_object_or_404(Video, pk=pk)
    
    # Increment total view count
    video.views_count += 1
    video.save(update_fields=['views_count'])
    
    # Update continue watching list in user session
    continue_watching = request.session.get('continue_watching', [])
    if pk in continue_watching:
        continue_watching.remove(pk)
    continue_watching.insert(0, pk)
    request.session['continue_watching'] = continue_watching[:6]
    request.session.modified = True

    # Check watchlist state for session
    is_in_watchlist = pk in request.session.get('watchlist', [])

    # Fetch active scheduled mid-roll ad cues for this film
    midrolls = video.midroll_ads.filter(ad__is_active=True)
    
    ad_cues = []
    for cue in midrolls:
        ad_cues.append({
            'time': cue.time_in_seconds,
            'ad_url': cue.advertisement.ad_video.url,
            'link': cue.advertisement.destination_url or '#',
            'title': cue.advertisement.title,
            'played': False
        })

    # Fetch related videos in same category
    related_videos = Video.objects.filter(category=video.category).exclude(pk=pk)[:4]
    if not related_videos.exists():
        related_videos = Video.objects.exclude(pk=pk)[:4]

    return render(request, 'web/video_detail.html', {
        'video': video,
        'related_videos': related_videos,
        'is_in_watchlist': is_in_watchlist,
        'ad_cues_json': json.dumps(ad_cues),
    })


def video_search(request):
    """HTMX endpoint filtering videos dynamically by query text AND category."""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    videos = Video.objects.all().order_by('-created_at')

    if query:
        videos = videos.filter(title__icontains=query)
    if category and category.lower() != 'all':
        videos = videos.filter(category__iexact=category)

    return render(request, 'web/partials/video_list.html', {'videos': videos})


def like_video(request, pk):
    """HTMX endpoint to increment likes instantly."""
    video = get_object_or_404(Video, pk=pk)
    video.likes_count += 1
    video.save(update_fields=['likes_count'])
    
    return HttpResponse(f'''
        <button hx-post="/video/{video.pk}/like/" 
                hx-target="#like-button-container" 
                hx-swap="innerHTML"
                class="flex items-center space-x-2 px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-xl transition font-bold text-sm shadow-lg">
            <span>❤️</span>
            <span>{video.likes_count} Likes</span>
        </button>
    ''')


def toggle_watchlist(request, pk):
    """HTMX endpoint to add or remove video from session watchlist."""
    watchlist = request.session.get('watchlist', [])
    
    if pk in watchlist:
        watchlist.remove(pk)
        is_added = False
    else:
        watchlist.append(pk)
        is_added = True

    request.session['watchlist'] = watchlist
    request.session.modified = True

    btn_text = "✓ In Watchlist" if is_added else "+ Add to Watchlist"
    btn_style = "bg-green-600 hover:bg-green-500 border-green-500" if is_added else "bg-white/10 hover:bg-white/20 border-white/20"

    return HttpResponse(f'''
        <button hx-post="/video/{pk}/watchlist/" 
                hx-target="#watchlist-button-container" 
                hx-swap="innerHTML"
                class="px-5 py-2.5 {btn_style} text-white font-bold rounded-xl backdrop-blur-md border transition text-sm">
            {btn_text}
        </button>
    ''')


@csrf_exempt
def update_playback_progress(request, video_id):
    """Called asynchronously by Video.js player beacon to track watch position."""
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        current_time = float(data.get('currentTime', 0))
        duration = float(data.get('duration', 0))
        
        is_completed = (current_time / duration) > 0.90 if duration > 0 else False
        
        WatchProgress.objects.update_or_create(
            user=request.user,
            video_id=video_id,
            defaults={
                'last_position_seconds': current_time,
                'duration_seconds': duration,
                'is_completed': is_completed
            }
        )
        return JsonResponse({'status': 'synced', 'resume_at': current_time})
    return JsonResponse({'error': 'unauthorized'}, status=401)