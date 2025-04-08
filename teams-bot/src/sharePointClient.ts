import { SPFetchClient } from "@pnp/nodejs";
import { spfi, SPFI, SPBrowser } from "@pnp/sp";
import "@pnp/sp/webs";
import "@pnp/sp/lists";
import "@pnp/sp/items";

interface IFaultCode {
    id: string;
    description: string;
    lastUpdated: Date;
    updatedBy: string;
}

export class SharePointClient {
    private sp: SPFI;
    private listName: string = "FaultCodes";

    constructor() {
        // Initialize SharePoint client with your site URL
        this.sp = spfi("https://your-tenant.sharepoint.com/sites/FaultCodes");
    }

    async getFaultCode(code: string): Promise<IFaultCode | null> {
        try {
            const items = await this.sp.web.lists
                .getByTitle(this.listName)
                .items
                .filter(`Code eq '${code}'`)
                .get();

            if (items.length === 0) {
                return null;
            }

            return {
                id: items[0].Code,
                description: items[0].Description,
                lastUpdated: new Date(items[0].Modified),
                updatedBy: items[0].Editor.Title
            };
        } catch (error) {
            console.error('Error fetching fault code:', error);
            return null;
        }
    }

    async getAllFaultCodes(): Promise<IFaultCode[]> {
        try {
            const items = await this.sp.web.lists
                .getByTitle(this.listName)
                .items
                .select('Code', 'Description', 'Modified', 'Editor/Title')
                .expand('Editor')
                .get();

            return items.map(item => ({
                id: item.Code,
                description: item.Description,
                lastUpdated: new Date(item.Modified),
                updatedBy: item.Editor.Title
            }));
        } catch (error) {
            console.error('Error fetching all fault codes:', error);
            return [];
        }
    }
} 