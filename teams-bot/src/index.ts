import {
    TeamsActivityHandler,
    CardFactory,
    TurnContext,
    MessageFactory
} from 'botbuilder';
import { SharePointClient } from './sharePointClient';

export class FaultCodeBot extends TeamsActivityHandler {
    private spClient: SharePointClient;

    constructor() {
        super();
        this.spClient = new SharePointClient();

        // Handle messages
        this.onMessage(async (context, next) => {
            const text = context.activity.text.trim().toUpperCase();
            
            // Handle commands
            if (text.startsWith('/')) {
                await this.handleCommand(context, text.substring(1));
            } 
            // Handle direct fault code queries
            else {
                await this.handleFaultCodeQuery(context, text);
            }
            await next();
        });
    }

    private async handleCommand(context: TurnContext, command: string) {
        switch (command.toLowerCase()) {
            case 'help':
                await this.sendHelp(context);
                break;
            case 'list':
                await this.listCodes(context);
                break;
            default:
                if (command.toLowerCase().startsWith('search ')) {
                    const code = command.substring(7).trim();
                    await this.handleFaultCodeQuery(context, code);
                } else {
                    await this.sendHelp(context);
                }
        }
    }

    private async handleFaultCodeQuery(context: TurnContext, code: string) {
        const faultCode = await this.spClient.getFaultCode(code);
        
        if (faultCode) {
            const card = CardFactory.adaptiveCard({
                type: 'AdaptiveCard',
                version: '1.0',
                body: [
                    {
                        type: 'TextBlock',
                        size: 'medium',
                        weight: 'bolder',
                        text: `Fault Code: ${code}`
                    },
                    {
                        type: 'TextBlock',
                        text: faultCode.description,
                        wrap: true
                    },
                    {
                        type: 'FactSet',
                        facts: [
                            {
                                title: 'Last Updated',
                                value: new Date(faultCode.lastUpdated).toLocaleDateString()
                            },
                            {
                                title: 'Updated By',
                                value: faultCode.updatedBy
                            }
                        ]
                    }
                ]
            });
            
            await context.sendActivity({ attachments: [card] });
        } else {
            await context.sendActivity(MessageFactory.text(
                `❌ Sorry, I couldn't find fault code "${code}". Use /help to see available commands.`
            ));
        }
    }

    private async sendHelp(context: TurnContext) {
        const helpText = `
👋 Welcome to the Fault Code Helper!

Available commands:
• Just type a fault code (e.g. "F001") to get its explanation
• /search [code] - Search for a specific fault code
• /list - Show all available fault codes
• /help - Show this help message

You can use me in:
• Personal chat
• Team channels
• Group chats
        `;
        
        await context.sendActivity(MessageFactory.text(helpText));
    }

    private async listCodes(context: TurnContext) {
        const codes = await this.spClient.getAllFaultCodes();
        
        if (codes.length === 0) {
            await context.sendActivity(MessageFactory.text('No fault codes found in the database.'));
            return;
        }

        const codesList = codes.map(code => `• ${code.id}: ${code.description.substring(0, 50)}...`).join('\n');
        
        await context.sendActivity(MessageFactory.text(
            `Available Fault Codes:\n\n${codesList}\n\nType a code or use /search [code] to get full details.`
        ));
    }
} 