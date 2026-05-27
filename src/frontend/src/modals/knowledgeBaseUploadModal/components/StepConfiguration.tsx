import ForwardedIconComponent from "@/components/common/genericIconComponent";
import ModelInputComponent, {
  type ModelOption,
} from "@/components/core/parameterRenderComponent/components/modelInputComponent";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/utils/utils";
import { ACCEPTED_FILE_TYPES } from "../constants";
import type { ColumnConfigRow } from "../types";

interface StepConfigurationProps {
  isAddSourcesMode: boolean;
  sourceName: string;
  onSourceNameChange: (value: string) => void;
  selectedEmbeddingModel: ModelOption[];
  onEmbeddingModelChange: (value: ModelOption[]) => void;
  embeddingModelOptions: ModelOption[];
  existingEmbeddingModel?: string;
  existingEmbeddingIcon?: string;
  chunkSize: number;
  onChunkSizeChange: (value: number) => void;
  chunkOverlap: number;
  onChunkOverlapChange: (value: number) => void;
  separator: string;
  onSeparatorChange: (value: string) => void;
  showAdvanced: boolean;
  toggleAdvanced: () => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onFolderSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  validationErrors?: Record<string, string>;
  onFieldChange?: () => void;
  columnConfig: ColumnConfigRow[];
  onColumnConfigChange: (value: ColumnConfigRow[]) => void;
}

export function StepConfiguration({
  isAddSourcesMode,
  sourceName,
  onSourceNameChange,
  selectedEmbeddingModel,
  onEmbeddingModelChange,
  embeddingModelOptions,
  existingEmbeddingModel,
  existingEmbeddingIcon,
  chunkSize,
  onChunkSizeChange,
  chunkOverlap,
  onChunkOverlapChange,
  separator,
  onSeparatorChange,
  showAdvanced,
  toggleAdvanced,
  onFileSelect,
  onFolderSelect,
  validationErrors = {},
  onFieldChange,
  columnConfig,
  onColumnConfigChange,
}: StepConfigurationProps) {
  return (
    <div className="relative">
      <div className="flex flex-col">
        {/* Name */}
        <div className="flex flex-col gap-2">
          <Label htmlFor="source-name" className="text-sm font-medium">
            名称 <span className="text-destructive">*</span>
          </Label>
          <Input
            id="source-name"
            placeholder="输入知识库名称"
            value={sourceName}
            onChange={(e) => {
              onSourceNameChange(e.target.value);
              onFieldChange?.();
            }}
            data-testid="kb-source-name-input"
            disabled={isAddSourcesMode}
            className={validationErrors.sourceName ? "border-destructive" : ""}
          />
          {validationErrors.sourceName && (
            <span className="text-xs text-destructive">
              {validationErrors.sourceName}
            </span>
          )}
        </div>

        {/* Model Selection */}
        <div className="flex flex-col gap-2 pt-4">
          <Label className="text-sm font-medium">
            嵌入模型 <span className="text-destructive">*</span>
          </Label>
          {isAddSourcesMode ? (
            <div className="flex h-10 w-full items-center gap-2 rounded-md border border-input bg-muted px-3 py-2 text-sm">
              <ForwardedIconComponent
                name={existingEmbeddingIcon || "Cpu"}
                className="h-4 w-4 shrink-0"
              />
              <span className="text-muted-foreground">
                {existingEmbeddingModel || "Unknown"}
              </span>
            </div>
          ) : (
            <div
              className={cn(
                "rounded-md",
                validationErrors.embeddingModel &&
                  "[&_button]:border-destructive",
              )}
            >
              <ModelInputComponent
                id="kb-embedding-model"
                value={selectedEmbeddingModel}
                editNode={false}
                disabled={false}
                handleOnNewValue={({ value }) => {
                  onEmbeddingModelChange(value);
                  onFieldChange?.();
                }}
                options={embeddingModelOptions}
                placeholder="选择嵌入模型"
                showEmptyState
              />
            </div>
          )}
          {validationErrors.embeddingModel && (
            <span className="text-xs text-destructive">
              {validationErrors.embeddingModel}
            </span>
          )}
        </div>

        {/* Hidden file inputs */}
        <input
          id="file-input"
          type="file"
          multiple
          className="hidden"
          onChange={onFileSelect}
          accept={ACCEPTED_FILE_TYPES}
        />
        <input
          id="folder-input"
          type="file"
          multiple
          className="hidden"
          onChange={onFolderSelect}
          accept={ACCEPTED_FILE_TYPES}
          {...({
            webkitdirectory: "",
            directory: "",
          } as React.HTMLAttributes<HTMLInputElement>)}
        />

        {/* Configure Sources - Animated */}
        <div
          className={cn(
            "grid transition-all duration-300 ease-in-out",
            showAdvanced
              ? "grid-rows-[1fr] opacity-100"
              : "grid-rows-[0fr] opacity-0",
          )}
        >
          <div className="overflow-hidden">
            <Separator className="my-4" />
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-2">
                <ForwardedIconComponent
                  name="LayoutGrid"
                  className="h-4 w-4 text-muted-foreground"
                />
                <span className="text-sm font-medium">
                  配置文件源
                  <span className="text-xs text-muted-foreground ml-1">
                    (最大上传1 GB)
                  </span>
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-2">
                  <Label className="text-xs text-muted-foreground">
                    文件源
                  </Label>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="outline"
                        data-testid="kb-browse-btn"
                        className={cn(
                          "w-full justify-between focus-visible:ring-1 focus-visible:ring-offset-0 focus-visible:ring-offset-background ",
                          validationErrors.files && "border-destructive",
                        )}
                      >
                        <span className="flex items-center gap-2">
                          <ForwardedIconComponent
                            name="Upload"
                            className="h-4 w-4"
                          />
                          添加文件源
                        </span>
                        <ForwardedIconComponent
                          name="ChevronDown"
                          className="h-4 w-4"
                        />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="start" className="w-[200px]">
                      <DropdownMenuItem
                        onClick={() =>
                          document.getElementById("file-input")?.click()
                        }
                      >
                        <ForwardedIconComponent
                          name="FileText"
                          className="mr-2 h-4 w-4"
                        />
                        上传文件
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() =>
                          document.getElementById("folder-input")?.click()
                        }
                      >
                        <ForwardedIconComponent
                          name="Folder"
                          className="mr-2 h-4 w-4"
                        />
                        上传文件夹
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>

                  {validationErrors.files && (
                    <span className="text-xs text-destructive">
                      {validationErrors.files}
                    </span>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  {/* <Label className="text-xs text-muted-foreground flex items-center gap-1">
                    Column Details
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="cursor-help">
                            <ForwardedIconComponent
                              name="Info"
                              className="h-3.5 w-3.5 text-muted-foreground"
                            />
                          </span>
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[260px]">
                          Configure column behavior for the knowledge base.
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <ColumnConfig
                    columnConfig={columnConfig}
                    onColumnConfigChange={onColumnConfigChange}
                  /> */}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chunking Settings - Animated */}
        <div
          className={cn(
            "grid transition-all duration-300 ease-in-out",
            showAdvanced
              ? "grid-rows-[1fr] opacity-100"
              : "grid-rows-[0fr] opacity-0",
          )}
        >
          <div className="overflow-hidden">
            <Separator className="my-4" />
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-2">
                <ForwardedIconComponent
                  name="Settings2"
                  className="h-4 w-4 text-muted-foreground"
                />
                <span className="text-sm font-medium">分块设置</span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Chunk Size */}
                <div className="flex flex-col gap-2">
                  <Label
                    htmlFor="chunk-size"
                    className="flex items-center gap-1 text-xs text-muted-foreground"
                  >
                    分块大小
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="cursor-help">
                            <ForwardedIconComponent
                              name="Info"
                              className="h-3.5 w-3.5 text-muted-foreground"
                            />
                          </span>
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[260px]">
                          每个分块的最大长度。文本先按分隔符拆分，然后合并分块至此大小。
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <Input
                    id="chunk-size"
                    type="number"
                    value={chunkSize}
                    onChange={(e) =>
                      onChunkSizeChange(Number(e.target.value) || 0)
                    }
                    min={1}
                    max={10000}
                    data-testid="kb-chunk-size-input"
                  />
                </div>

                {/* Chunk Overlap */}
                <div className="flex flex-col gap-2">
                  <Label
                    htmlFor="chunk-overlap"
                    className="flex items-center gap-1 text-xs text-muted-foreground"
                  >
                    分块重叠
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="cursor-help">
                            <ForwardedIconComponent
                              name="Info"
                              className="h-3.5 w-3.5 text-muted-foreground"
                            />
                          </span>
                        </TooltipTrigger>
                        <TooltipContent className="max-w-[260px]">
                          分块之间的重叠字符数。
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Label>
                  <Input
                    id="chunk-overlap"
                    type="number"
                    value={chunkOverlap}
                    onChange={(e) =>
                      onChunkOverlapChange(Number(e.target.value) || 0)
                    }
                    min={0}
                    max={chunkSize - 1}
                    data-testid="kb-chunk-overlap-input"
                  />
                </div>
              </div>

              {/* Separator */}
              <div className="flex flex-col gap-2">
                <Label
                  htmlFor="separator"
                  className="flex items-center gap-1 text-xs text-muted-foreground"
                >
                  分隔符
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="cursor-help">
                          <ForwardedIconComponent
                            name="Info"
                            className="h-3.5 w-3.5 text-muted-foreground"
                          />
                        </span>
                      </TooltipTrigger>
                      <TooltipContent className="max-w-[260px]">
                        用于拆分的字符。使用 \n 表示换行。示例：\n\n
                        用于段落，\n 用于行，. 用于句子。留空表示无分隔符。
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </Label>
                <Input
                  id="separator"
                  placeholder="\n"
                  value={separator}
                  onChange={(e) => onSeparatorChange(e.target.value)}
                  data-testid="kb-separator-input"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
