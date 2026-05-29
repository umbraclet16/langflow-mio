// ERROR
export const MISSED_ERROR_ALERT = "哎呀！看起来你遗漏了什么";
export const INCOMPLETE_LOOP_ERROR_ALERT =
  "流程存在未完成的循环。请检查连接后重试。";
export const INVALID_FILE_ALERT = "请选择有效文件。仅允许以下文件类型：";
export const CONSOLE_ERROR_MSG = "上传文件时发生错误";
export const CONSOLE_SUCCESS_MSG = "文件上传成功";
export const INFO_MISSING_ALERT = "哎呀！看起来你遗漏了一些必填信息：";
export const FUNC_ERROR_ALERT = "函数中存在错误";
export const IMPORT_ERROR_ALERT = "导入中存在错误";
export const BUG_ALERT = "出了点问题，请重试";
export const CODE_ERROR_ALERT = "代码存在问题，请检查";
export const CHAT_ERROR_ALERT = "请重新构建流程后再使用聊天功能。";
export const MSG_ERROR_ALERT = "发送消息时出错";
export const PROMPT_ERROR_ALERT = "提示词存在问题，请检查";
export const API_ERROR_ALERT = "保存API密钥时出错，请重试。";
export const USER_DEL_ERROR_ALERT = "删除用户时出错";
export const USER_EDIT_ERROR_ALERT = "编辑用户时出错";
export const USER_ADD_ERROR_ALERT = "添加新用户时出错";
export const SIGNIN_ERROR_ALERT = "登录时出错";
export const DEL_KEY_ERROR_ALERT = "删除密钥时出错";
export const DEL_KEY_ERROR_ALERT_PLURAL = "删除密钥时出错";
export const UPLOAD_ERROR_ALERT = "上传文件时出错";
export const WRONG_FILE_ERROR_ALERT = "文件类型无效";
export const UPLOAD_ALERT_LIST = "请上传JSON文件";
export const INVALID_SELECTION_ERROR_ALERT = "选择无效";
export const EDIT_PASSWORD_ERROR_ALERT = "修改密码时出错";
export const EDIT_PASSWORD_ALERT_LIST = "密码不匹配";
export const SAVE_ERROR_ALERT = "保存更改时出错";
export const PROFILE_PICTURES_GET_ERROR_ALERT = "获取头像时出错";
export const SIGNUP_ERROR_ALERT = "注册时出错";
export const APIKEY_ERROR_ALERT = "API密钥错误"; // pragma: allowlist secret
export const NOAPI_ERROR_ALERT =
  "您没有API密钥。请添加一个以使用Langflow商店。";
export const INVALID_API_ERROR_ALERT =
  "您的API密钥无效。请添加有效的API密钥以使用Langflow商店。";
export const COMPONENTS_ERROR_ALERT = "获取组件时出错。";

// NOTICE # pragma: allowlist secret
export const NOCHATOUTPUT_NOTICE_ALERT = "流程中没有ChatOutput组件。";
export const API_WARNING_NOTICE_ALERT =
  "警告：关键数据，JSON文件可能包含API密钥。";
export const COPIED_NOTICE_ALERT = "API密钥已复制！";
export const TEMP_NOTICE_ALERT = "您的模板没有任何变量。";

// SUCCESS
export const CODE_SUCCESS_ALERT = "代码已准备好运行";
export const PROMPT_SUCCESS_ALERT = "提示词已就绪";
export const API_SUCCESS_ALERT = "成功！您的API密钥已保存。";
export const USER_DEL_SUCCESS_ALERT = "成功！用户已删除！";
export const USER_EDIT_SUCCESS_ALERT = "成功！用户已编辑！";
export const USER_ADD_SUCCESS_ALERT = "成功！新用户已添加！";
export const DEL_KEY_SUCCESS_ALERT = "成功！密钥已删除！";
export const DEL_KEY_SUCCESS_ALERT_PLURAL = "成功！密钥已删除！";
export const FLOW_BUILD_SUCCESS_ALERT = `流程构建成功`;
export const SAVE_SUCCESS_ALERT = "更改已成功保存！";
export const INVALID_FILE_SIZE_ALERT = (maxSizeMB) => {
  return `文件太大。请选择小于${maxSizeMB}MB的文件。`;
};
