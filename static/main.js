// 从本地获取历史记录
function getHistory() {
    const historyJSON = localStorage.getItem('watch_history');
    if (historyJSON) {
        return JSON.parse(historyJSON);
    }
    return [];
}

// 记录当前观看过的视频 (去重)
function addVideoToHistory(videoId) {
    let history = getHistory();
    // 移除已存在的该视频（为了将其放到列表最后代表最新观看）
    history = history.filter(id => id !== videoId);
    history.push(videoId);
    // 限定只保留最近的20个观看记录
    if (history.length > 20) {
        history.shift();
    }
    localStorage.setItem('watch_history', JSON.stringify(history));
}

// 清理历史记录
function clearHistory() {
    localStorage.removeItem('watch_history');
    alert("观看历史已清空！");
    window.location.reload();
}