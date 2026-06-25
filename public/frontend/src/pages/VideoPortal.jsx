import { useEffect, useState, useRef } from 'react'
import { useSelector } from 'react-redux'
import api from '../services/api'

const VideoPortal = () => {
  const [videos, setVideos] = useState([])
  const [selectedVideo, setSelectedVideo] = useState(null)
  const user = useSelector(state => state.auth.user)
  const videoRef = useRef(null)
  const [watermark, setWatermark] = useState({ name: '', email: '', time: '' })

  useEffect(() => {
    const loadVideos = async () => {
      try {
        const res = await api.get('/videos')
        setVideos(res.data)
        if (res.data.length > 0) setSelectedVideo(res.data[0])
      } catch (err) {
        console.error(err)
      }
    }
    loadVideos()
  }, [])

  useEffect(() => {
    if (!user) return
    const updateTime = () => {
      setWatermark({
        name: user.full_name,
        email: user.email,
        time: new Date().toLocaleString()
      })
    }
    updateTime()
    const interval = setInterval(updateTime, 1000)
    return () => clearInterval(interval)
  }, [user])

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (
        e.key === 'F12' ||
        (e.ctrlKey && e.shiftKey && ['I', 'J', 'C'].includes(e.key)) ||
        (e.ctrlKey && ['u', 's', 'U', 'S'].includes(e.key))
      ) {
        e.preventDefault()
      }
    }

    const handleContextMenu = (e) => e.preventDefault()
    const handleCopy = (e) => e.preventDefault()
    const handleCut = (e) => e.preventDefault()
    const handlePaste = (e) => e.preventDefault()

    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('contextmenu', handleContextMenu)
    document.addEventListener('copy', handleCopy)
    document.addEventListener('cut', handleCut)
    document.addEventListener('paste', handlePaste)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('contextmenu', handleContextMenu)
      document.removeEventListener('copy', handleCopy)
      document.removeEventListener('cut', handleCut)
      document.removeEventListener('paste', handlePaste)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-8 text-center">Trading Video Portal</h1>
        <div className="flex gap-8">
          <div className="w-1/3">
            <h2 className="text-xl font-semibold mb-4">Videos</h2>
            <div className="space-y-2">
              {videos.map(video => (
                <div
                  key={video.id}
                  onClick={() => setSelectedVideo(video)}
                  className={`p-4 bg-white rounded-lg cursor-pointer ${selectedVideo?.id === video.id ? 'ring-2 ring-blue-500' : ''}`}
                >
                  <h3 className="font-medium">{video.title}</h3>
                </div>
              ))}
            </div>
          </div>
          <div className="w-2/3">
            {selectedVideo && (
              <div className="relative">
                <div
                  className="absolute top-0 left-0 w-full h-full pointer-events-none z-10"
                  style={{
                    background: `repeating-linear-gradient(
                      45deg,
                      transparent,
                      transparent 100px,
                      rgba(255,255,255,0.1) 100px,
                      rgba(255,255,255,0.1) 200px
                    )`
                  }}
                >
                  {[...Array(20)].map((_, i) => (
                    <div
                      key={i}
                      className="absolute text-xs text-gray-300 opacity-30"
                      style={{
                        top: `${Math.random() * 90}%`,
                        left: `${Math.random() * 90}%`,
                        transform: `rotate(${Math.random() * 30 - 15}deg)`
                      }}
                    >
                      {watermark.name} - {watermark.email} - {watermark.time}
                    </div>
                  ))}
                </div>
                <video
                  ref={videoRef}
                  src={selectedVideo.video_url}
                  controls
                  className="w-full rounded-lg"
                  disablePictureInPicture
                  controlsList="nodownload"
                />
                <h2 className="text-2xl font-bold mt-4">{selectedVideo.title}</h2>
                <p className="text-gray-600 mt-2">{selectedVideo.description}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default VideoPortal
