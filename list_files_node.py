# list_files_node.py
import os
import hashlib
from typing import List, Optional, Tuple

# ============================================================
# 扩展名预设常量
# ============================================================
IMAGE_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif",
    ".gif", ".avif", ".jfif", ".pjpeg", ".pjp", ".svg", ".ico"
]

VIDEO_EXTENSIONS = [
    ".mp4", ".webm", ".avi", ".mov", ".mkv", ".flv", ".wmv",
    ".m4v", ".mpg", ".mpeg", ".3gp", ".ogv", ".ts", ".mts"
]

MODEL_EXTENSIONS = [
    ".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".onnx",
    ".pb", ".pkl", ".gguf", ".ggml", ".engine", ".trt"
]

EXTENSION_PRESETS = {
    "images": IMAGE_EXTENSIONS,
    "videos": VIDEO_EXTENSIONS,
    "models": MODEL_EXTENSIONS,
    "all": None,  # None = 所有文件
}

# ============================================================
# 工具函数
# ============================================================

def parse_extensions(custom_extensions: str) -> Optional[List[str]]:
    """解析用户自定义扩展名字符串"""
    if not custom_extensions or not custom_extensions.strip():
        return None
    exts = []
    for part in custom_extensions.split(","):
        ext = part.strip().lower()
        if ext:
            if not ext.startswith("."):
                ext = "." + ext
            exts.append(ext)
    return exts if exts else None


def get_sorted_file_list(
    directory: str,
    extensions: Optional[List[str]],
    skip_first: int = 0,
    select_every_nth: int = 1,
    file_limit: int = 0,
    sort_by: str = "name"
) -> List[str]:
    """获取目录下排序后的文件完整路径列表"""
    if not os.path.isdir(directory):
        return []

    files = []
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                if extensions is None:
                    files.append(entry.path)
                else:
                    _, ext = os.path.splitext(entry.name)
                    if ext.lower() in extensions:
                        files.append(entry.path)
    except (PermissionError, OSError) as e:
        print(f"[ListFilesFromDirectory] Error scanning directory: {e}")
        return []

    # 排序
    if sort_by == "name":
        files.sort(key=lambda p: os.path.basename(p).lower())
    elif sort_by == "date_modified":
        files.sort(key=lambda p: os.path.getmtime(p))
    elif sort_by == "size":
        files.sort(key=lambda p: os.path.getsize(p))
    # "none" = 不排序

    # 跳过前 N 个
    if skip_first > 0:
        files = files[skip_first:]

    # 每隔 N 个选一个
    if select_every_nth > 1:
        files = files[::select_every_nth]

    # 限制数量
    if file_limit > 0:
        files = files[:file_limit]

    return files


def calculate_directory_hash(
    directory: str,
    extensions: Optional[List[str]],
    skip_first: int,
    select_every_nth: int,
    file_limit: int,
    sort_by: str
) -> str:
    """计算目录文件列表的哈希值，用于检测变化"""
    files = get_sorted_file_list(
        directory, extensions, skip_first,
        select_every_nth, file_limit, sort_by
    )
    m = hashlib.sha256()
    for filepath in files:
        stat_info = os.stat(filepath)
        m.update(filepath.encode('utf-8'))
        m.update(str(stat_info.st_mtime).encode('utf-8'))
        m.update(str(stat_info.st_size).encode('utf-8'))
    return m.hexdigest()


# ============================================================
# 自定义节点类
# ============================================================

class ListFilesFromDirectory:
    """
    📂 文件遍历器 - 从目录中逐个输出文件路径。

    功能：
    - 遍历指定目录下的文件，按扩展名过滤
    - 支持预设扩展名（图片、视频、模型）或自定义
    - 支持排序、跳过、间隔选取
    - 配合 ComfyUI 的 for 循环节点使用（通过 index 控制）
    - 兼容 VHS 风格的 meta_batch 批量处理模式
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": (
                    "STRING",
                    {
                        "default": "",
                        "placeholder": "X:/path/to/your/files",
                        "multiline": False,
                        "dynamicPrompts": False,
                    }
                ),
                "extension_preset": (
                    ["images", "videos", "models", "all", "custom"],
                    {"default": "images"}
                ),
            },
            "optional": {
                "custom_extensions": (
                    "STRING",
                    {
                        "default": ".jpg,.png,.webp",
                        "placeholder": ".ext1,.ext2,.ext3",
                        "multiline": False,
                    }
                ),
                "file_limit": (
                    "INT",
                    {
                        "default": 0, "min": 0, "max": 9999999,
                        "step": 1, "display": "number"
                    }
                ),
                "skip_first": (
                    "INT",
                    {
                        "default": 0, "min": 0, "max": 9999999,
                        "step": 1, "display": "number"
                    }
                ),
                "select_every_nth": (
                    "INT",
                    {
                        "default": 1, "min": 1, "max": 9999999,
                        "step": 1, "display": "number"
                    }
                ),
                "sort_by": (
                    ["name", "date_modified", "size", "none"],
                    {"default": "name"}
                ),
                "index": (
                    "INT",
                    {
                        "default": 0, "min": 0, "max": 9999999,
                        "step": 1, "display": "number",
                        "label": "文件索引 (配合循环节点使用)"
                    }
                ),
                "meta_batch": ("VHS_BatchManager",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("STRING", "INT", "STRING", "INT")
    RETURN_NAMES = ("file_path", "total_count", "filename", "current_index")
    OUTPUT_IS_LIST = (False, False, False, False)

    FUNCTION = "get_file"
    CATEGORY = "Batch Tools 🐟"

    # ----------------------------------------------------------
    # 核心逻辑
    # ----------------------------------------------------------

    def get_file(self, directory: str, extension_preset: str,
                 custom_extensions: str = "",
                 file_limit: int = 0, skip_first: int = 0,
                 select_every_nth: int = 1, sort_by: str = "name",
                 index: int = 0, meta_batch=None, unique_id=None, **kwargs):
        """获取文件路径"""
        # 解析扩展名
        extensions = self._resolve_extensions(extension_preset, custom_extensions)

        # 获取文件列表
        files = get_sorted_file_list(
            directory, extensions, skip_first,
            select_every_nth, file_limit, sort_by
        )

        total_count = len(files)

        # Batch 模式
        if meta_batch is not None:
            return self._handle_batch_mode(
                files, meta_batch, unique_id, total_count
            )

        # 索引模式
        return self._handle_index_mode(files, index, total_count)

    def _handle_index_mode(self, files: List[str], index: int,
                           total_count: int) -> Tuple[str, int, str, int]:
        """索引模式：根据 index 输出指定文件"""
        if total_count == 0:
            print("[ListFilesFromDirectory] ⚠️ No files found.")
            return ("", 0, "", 0)

        current_index = max(0, min(index, total_count - 1))
        file_path = files[current_index]
        filename = os.path.basename(file_path)

        return (file_path, total_count, filename, current_index)

    def _handle_batch_mode(self, files: List[str], meta_batch,
                           unique_id: str, total_count: int) -> Tuple[str, int, str, int]:
        """Batch 模式：逐帧输出文件路径"""
        if unique_id is None or unique_id not in meta_batch.inputs:
            gen = self._file_path_generator(files)
            meta_batch.inputs[unique_id] = gen
            meta_batch.total_frames = min(meta_batch.total_frames, total_count)

        gen = meta_batch.inputs[unique_id]
        current_index = 0
        file_path = ""

        try:
            file_path = next(gen)
            current_index = files.index(file_path) if file_path in files else 0
        except StopIteration:
            meta_batch.inputs.pop(unique_id, None)
            meta_batch.has_closed_inputs = True
            file_path = files[-1] if files else ""
            current_index = total_count - 1 if files else 0

        filename = os.path.basename(file_path) if file_path else ""
        return (file_path, total_count, filename, current_index)

    @staticmethod
    def _file_path_generator(files: List[str]):
        """生成器：逐个 yield 文件路径"""
        for f in files:
            yield f

    @classmethod
    def _resolve_extensions(cls, extension_preset: str,
                            custom_extensions: str) -> Optional[List[str]]:
        """解析扩展名设置"""
        if extension_preset == "custom":
            return parse_extensions(custom_extensions)
        return EXTENSION_PRESETS.get(extension_preset)

    # ----------------------------------------------------------
    # ComfyUI 生命周期钩子
    # ----------------------------------------------------------

    @classmethod
    def IS_CHANGED(cls, directory: str, extension_preset: str,
                   custom_extensions: str = "",
                   file_limit: int = 0, skip_first: int = 0,
                   select_every_nth: int = 1, sort_by: str = "name",
                   index: int = 0, **kwargs):
        """检测目录内容是否发生变化"""
        if not directory or not os.path.isdir(directory):
            return False

        extensions = cls._resolve_extensions(extension_preset, custom_extensions)
        return calculate_directory_hash(
            directory, extensions, skip_first,
            select_every_nth, file_limit, sort_by
        )

    @classmethod
    def VALIDATE_INPUTS(cls, directory: str, extension_preset: str, **kwargs):
        """验证输入参数的有效性"""
        if not directory or not directory.strip():
            return "❌ 目录路径不能为空！"

        if not os.path.isdir(directory):
            return f"❌ 目录不存在或无法访问: {directory}"

        try:
            os.listdir(directory)
        except PermissionError:
            return f"❌ 没有权限读取目录: {directory}"
        except OSError as e:
            return f"❌ 无法访问目录: {e}"

        return True


# ============================================================
# 节点注册映射
# ============================================================
NODE_CLASS_MAPPINGS = {
    "ListFilesFromDirectory": ListFilesFromDirectory,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ListFilesFromDirectory": "📂 File List from Directory",
}