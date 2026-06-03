const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileBtn = document.getElementById('fileBtn');
const mdInput = document.getElementById('mdInput');
const convertBtn = document.getElementById('convertBtn');
const previewFrame = document.getElementById('previewFrame');
const status = document.getElementById('status');
const downloadBtn = document.getElementById('downloadBtn');
const thumbnails = document.getElementById('thumbnails');

// File upload
dropzone.addEventListener('click', () => fileInput.click());
fileBtn.addEventListener('click', (e) => { e.stopPropagation(); fileInput.click(); });

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) readFile(file);
});

fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) readFile(file);
});

function readFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    mdInput.value = e.target.result;
    status.textContent = `📎 已加载: ${file.name}`;
  };
  reader.readAsText(file);
}

// Convert
convertBtn.addEventListener('click', async () => {
  const mdText = mdInput.value.trim();
  if (!mdText) {
    status.textContent = '❌ 请先上传或粘贴 Markdown 文本';
    return;
  }

  const generateCover = document.getElementById('coverCheck').checked;
  const generateSections = document.getElementById('sectionsCheck').checked;
  const generateInfographic = document.getElementById('infographicCheck').checked;
  const enhancePrompts = document.getElementById('enhanceCheck').checked;
  const imageSize = document.getElementById('imageSize').value;

  const useAI = generateCover || generateSections || generateInfographic;
  status.textContent = useAI ? '🎨 正在生成图片，请稍候...' : '⏳ 转换中...';
  convertBtn.disabled = true;
  thumbnails.innerHTML = '';

  const formData = new FormData();
  formData.append('md_text', mdText);
  formData.append('generate_cover', generateCover);
  formData.append('generate_sections', generateSections);
  formData.append('generate_infographic', generateInfographic);
  formData.append('enhance_prompts', enhancePrompts);
  formData.append('image_size', imageSize);

  try {
    const resp = await fetch('/convert', { method: 'POST', body: formData });
    const data = await resp.json();

    if (data.error) {
      status.textContent = `❌ 错误: ${data.error}`;
      return;
    }

    previewFrame.src = data.preview_url;
    status.textContent = `✅ 转换完成！图片 ${data.images.length} 张 · Job: ${data.job_id}`;

    downloadBtn.href = data.preview_url;
    downloadBtn.style.display = 'inline-block';
    downloadBtn.download = `output_${data.job_id}.html`;

    data.images.forEach(url => {
      const img = document.createElement('img');
      img.src = url;
      img.title = url.split('/').pop();
      img.onclick = () => window.open(url, '_blank');
      thumbnails.appendChild(img);
    });

  } catch (err) {
    status.textContent = `❌ 请求失败: ${err.message}`;
  } finally {
    convertBtn.disabled = false;
  }
});
