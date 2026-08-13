# 📂 File List from Directory

一个简单实用的 ComfyUI 自定义节点，用于**遍历指定目录下的文件，逐个输出文件完整路径**，方便批量处理图片、视频、模型等文件。

---

## ✨ 功能特性

- 🔍 **目录遍历**：扫描指定目录下的所有文件
- 🎯 **扩展名过滤**：内置图片、视频、模型扩展名预设，也支持自定义
- 🔄 **自动递增输出**：每次运行自动输出下一个文件，无需手动改参数
- 🎛️ **灵活排序**：支持按名称、修改日期、文件大小排序
- 📊 **状态感知**：目录内容变化时自动重置遍历进度
- 🔁 **循环模式**：遍历完所有文件后自动回到第一个
- 🧩 **VHS 兼容**：可接入 VHS_BatchManager 实现批量处理

---

## 📦 安装方法

### 方式一：Git Clone（推荐）

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/yourname/comfy-list-files.git
```

### 方式二：手动安装

1. 在 `ComfyUI/custom_nodes/` 下创建文件夹 `comfy-list-files`
2. 将以下文件放入该文件夹：

```
comfy-list-files/
├── __init__.py            # 节点注册入口
└── list_files_node.py     # 节点核心逻辑
```

3. **重启 ComfyUI**

---

## 🚀 快速开始

### 场景一：配合 Batch Count 批量处理（推荐）

这是最常用的方式，**无需连接任何额外节点**。

```
1. 添加节点：Batch Tools 🐟 → 📂 File List from Directory
2. 设置 directory 为你的目标目录
3. 选择 extension_preset（如图片）
4. 保持 index = -1（自动递增模式）
5. 在 ComfyUI 队列面板设置 Batch Count = 5
6. 点击 Queue Prompt
```

效果：5 次运行依次输出目录中第 1、2、3、4、5 个文件的路径。

```
┌─────────────────────┐
│  Batch Count = 5    │
│  ┌───────────────┐  │
│  │ Run 1 → 文件1  │  │
│  │ Run 2 → 文件2  │  │
│  │ Run 3 → 文件3  │  │
│  │ Run 4 → 文件4  │  │
│  │ Run 5 → 文件5  │  │
│  └───────────────┘  │
└─────────────────────┘
```

### 场景二：配合 For 循环节点

如果你安装了带循环节点的扩展（如 Efficiency Nodes），可以这样用：

```
[For Loop] --index--> [File List from Directory] --file_path--> [你的处理节点]
```

### 场景三：VHS BatchManager 兼容

连接 `meta_batch` 到 VHS 的 BatchManager 节点，实现逐帧输出：

```
[VHS_BatchManager] --meta_batch--> [File List from Directory] --file_path--> [处理节点]
```

---

## 📝 节点参数说明

### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `directory` | STRING | 要遍历的目录路径，如 `D:/images` 或 `/home/user/videos` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `extension_preset` | COMBO | `images` | 扩展名预设：`images` / `videos` / `models` / `all` / `custom` |
| `custom_extensions` | STRING | `.jpg,.png,.webp` | 自定义扩展名（逗号分隔），仅 `custom` 预设时生效 |
| `file_limit` | INT | `0` | 最大输出文件数，`0` = 不限制 |
| `skip_first` | INT | `0` | 跳过前 N 个文件 |
| `select_every_nth` | INT | `1` | 每隔 N 个选一个（如 `2` = 取第 1,3,5... 个） |
| `sort_by` | COMBO | `name` | 排序方式：`name` / `date_modified` / `size` / `none` |
| `loop_mode` | BOOLEAN | `true` | 遍历完所有文件后是否循环回到第一个 |
| `index` | INT | `-1` | `-1` = 自动递增；`>=0` = 手动指定输出第几个文件 |
| `meta_batch` | VHS_BatchManager | - | 可选，VHS 批量管理器 |

---

## 📤 输出说明

| 输出 | 类型 | 说明 |
|------|------|------|
| `file_path` | STRING | 当前文件的**完整路径** |
| `total_count` | INT | 目录中匹配的文件**总数** |
| `filename` | STRING | 当前文件的**文件名**（不含路径） |
| `current_index` | INT | 当前文件的**索引**（从 0 开始） |

---

## 🖼️ 扩展名预设

| 预设 | 包含的扩展名 |
|------|-------------|
| **images** | `.jpg` `.jpeg` `.png` `.webp` `.bmp` `.tiff` `.tif` `.gif` `.avif` `.jfif` `.pjpeg` `.pjp` `.svg` `.ico` |
| **videos** | `.mp4` `.webm` `.avi` `.mov` `.mkv` `.flv` `.wmv` `.m4v` `.mpg` `.mpeg` `.3gp` `.ogv` `.ts` `.mts` |
| **models** | `.safetensors` `.ckpt` `.pt` `.pth` `.bin` `.onnx` `.pb` `.pkl` `.gguf` `.ggml` `.engine` `.trt` |
| **all** | 所有文件（不过滤） |
| **custom** | 用户自定义，如 `.jpg,.png,.webp` |

---

## 🔧 实用示例

### 示例 1：批量处理图片

```
directory:      D:/photos
extension_preset: images
index:          -1 (自动递增)
Batch Count:    10
```

### 示例 2：只处理第 3~8 个模型文件

```
directory:      D:/models
extension_preset: models
skip_first:     2        ← 跳过前 2 个
file_limit:     6        ← 最多输出 6 个
index:          -1
```

### 示例 3：处理自定义扩展名文件

```
directory:      D:/data
extension_preset: custom
custom_extensions: .txt,.md,.json
sort_by:        date_modified   ← 按修改时间排序
```

### 示例 4：手动指定第 3 个文件

```
directory:      D:/images
index:          2   ← 输出第 3 个文件（索引从 0 开始）
```

---

## ⚠️ 常见问题

### Q1：为什么设置 Batch Count 后每次输出的都是第一个文件？

请检查 `index` 是否为 `-1`。如果 `index` 被设置成 `0` 或连接到其他节点，节点会固定输出对应索引的文件。

### Q2：节点输出的文件路径是绝对路径吗？

是的，`file_path` 输出的是文件的**完整绝对路径**，可以直接用于加载、读取等操作。

### Q3：目录中的文件变化后，遍历进度会自动重置吗？

会。节点会检测目录内容（文件名、修改时间、大小）的变化，一旦发生变化，自动从头开始遍历。

### Q4：遍历完所有文件后会怎样？

默认开启 `loop_mode`，会回到第一个文件继续循环。如果关闭 `loop_mode`，则停在最后一个文件。

### Q5：支持子目录递归吗？

当前版本**不支持**递归子目录，只扫描指定目录的直接子文件。如有需要可在 GitHub 提 Issue。

### Q6：中文路径支持吗？

支持。使用 UTF-8 编码，中英文路径均可正常处理。

---

## 📄 更新日志

### v1.0.0 (2026-08-13)

- 🎉 首次发布
- 支持目录遍历与扩展名过滤
- 支持自动递增模式（配合 Batch Count）
- 支持手动索引模式（配合循环节点）
- 支持 VHS BatchManager 兼容
- 内置图片、视频、模型扩展名预设

---


---

## 🙏 致谢

- 参考了 [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite) 的节点设计
- 参考了 ComfyUI 自定义节点开发文档
```
