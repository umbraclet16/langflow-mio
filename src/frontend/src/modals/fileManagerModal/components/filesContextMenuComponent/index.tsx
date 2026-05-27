import { type ReactNode, useState } from "react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useDeleteFileV2 } from "@/controllers/API/queries/file-management/use-delete-file";
import { useDuplicateFileV2 } from "@/customization/hooks/use-custom-duplicate-file";
import { useCustomHandleSingleFileDownload } from "@/customization/hooks/use-custom-handle-single-file-download";
import ConfirmationModal from "@/modals/confirmationModal";
import useAlertStore from "@/stores/alertStore";
import type { FileType } from "@/types/file_management";

export default function FilesContextMenuComponent({
  children,
  file,
  handleRename,
  simplified,
}: {
  children: ReactNode;
  file: FileType;
  handleRename: (id: string, name: string) => void;
  simplified?: boolean;
}) {
  const isLocal = file.provider == null;
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);

  const setSuccessData = useAlertStore((state) => state.setSuccessData);

  const { handleSingleDownload } = useCustomHandleSingleFileDownload(file);

  const { mutate: deleteFile } = useDeleteFileV2({
    id: file.id,
  });

  const { mutate: duplicateFile } = useDuplicateFileV2({
    id: file.id,
    filename: file.name,
    type: file.path.split(".").pop() || "",
  });

  const handleSelectOptionsChange = (option: string) => {
    switch (option) {
      case "rename":
        handleRename(file.id, file.name);
        break;
      case "replace":
        // TODO: Implement replace file
        console.warn("replace");
        break;
      case "download":
        handleSingleDownload();
        break;
      case "delete":
        setShowDeleteConfirmation(true);
        break;
      case "duplicate":
        duplicateFile();
        break;
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>{children}</DropdownMenuTrigger>
        <DropdownMenuContent sideOffset={0} side="bottom" className="-ml-24">
          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation();
              handleSelectOptionsChange("rename");
            }}
            className="cursor-pointer"
            data-testid="btn-rename-file"
          >
            <ForwardedIconComponent
              name="SquarePen"
              aria-hidden="true"
              className="mr-2 h-4 w-4"
            />
            重命名
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation();
              handleSelectOptionsChange("download");
            }}
            className="cursor-pointer"
            data-testid="btn-download-json"
          >
            <ForwardedIconComponent
              name="Download"
              aria-hidden="true"
              className="mr-2 h-4 w-4"
            />
            下载
          </DropdownMenuItem>
          {!simplified && (
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                handleSelectOptionsChange("duplicate");
              }}
              className="cursor-pointer"
              data-testid="btn-duplicate-flow"
            >
              <ForwardedIconComponent
                name="CopyPlus"
                aria-hidden="true"
                className="mr-2 h-4 w-4"
              />
              复制
            </DropdownMenuItem>
          )}
          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation();
              handleSelectOptionsChange("delete");
            }}
            className="cursor-pointer text-destructive"
            data-testid="btn-delete-file"
          >
            <ForwardedIconComponent
              name={isLocal ? "Trash2" : "ListX"}
              aria-hidden="true"
              className="mr-2 h-4 w-4"
            />
            {isLocal ? "删除" : "移除"}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <ConfirmationModal
        open={showDeleteConfirmation}
        onClose={() => setShowDeleteConfirmation(false)}
        onCancel={() => setShowDeleteConfirmation(false)}
        title={isLocal ? "删除文件" : "移除文件"}
        titleHeader={`确定要${isLocal ? "删除" : "移除"} "${file.name}" 吗?`}
        cancelText="取消"
        size="x-small"
        confirmationText={isLocal ? "删除" : "移除"}
        icon={isLocal ? "Trash2" : "ListX"}
        destructive
        onConfirm={() => {
          deleteFile();
          setSuccessData({
            title: "文件已成功删除",
          });
          setShowDeleteConfirmation(false);
        }}
      >
        <ConfirmationModal.Content>
          <div className="text-sm text-muted-foreground">
            {isLocal
              ? "This action cannot be undone. The file will be permanently deleted."
              : "This will remove the file from your list. You can add it back later if needed."}
          </div>
        </ConfirmationModal.Content>
      </ConfirmationModal>
    </>
  );
}
