import type { UseQueryResult } from "@tanstack/react-query";
import type { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

export interface MCPConfigResponse {
  source: "local" | "agent_platform";
  agent_platform_url: string | null;
}

export const useGetMCPConfig: useQueryFunctionType<
  undefined,
  MCPConfigResponse
> = (options?) => {
  const { query } = UseRequestProcessor();

  const getMCPConfigFn = async (): Promise<MCPConfigResponse> => {
    const res = await api.get<MCPConfigResponse>(
      getURL("MCP_CONFIG", {}, true),
    );
    return res.data;
  };

  const queryResult: UseQueryResult<MCPConfigResponse, any> = query(
    ["useGetMCPConfig"],
    getMCPConfigFn,
    {
      refetchOnWindowFocus: false,
      ...options,
    },
  );

  return queryResult;
};
