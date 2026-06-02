import discord
from discord import app_commands
from discord.ext import commands
import gspread
import os
import json
from datetime import datetime

# 1. Configuração Segura: Lê credenciais das Variáveis de Ambiente
creds_json = os.environ.get("GCP_SERVICE_ACCOUNT")
creds_dict = json.loads(creds_json)

# Conexão com Google Sheets usando dicionário
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open("SistemaAprovacoes").sheet1

intents = discord.Intents.default()
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # ID do seu servidor
    MY_GUILD = discord.Object(id=1511291920566063145) 
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print(f"Bot online e comando /registrar sincronizado!")

@bot.tree.command(name="registrar", description="Registrar usuário e banir se um motivo for fornecido")
@app_commands.describe(
    id_usuario="O ID do usuário para registrar", 
    status="Escolha Aprovado ou Reprovado",
    motivo="[OPCIONAL] Se preenchido, o usuário será banido deste servidor"
)
@app_commands.choices(status=[
    app_commands.Choice(name="Aprovado", value="Aprovado"),
    app_commands.Choice(name="Reprovado", value="Reprovado")
])
async def registrar(interaction: discord.Interaction, id_usuario: str, status: app_commands.Choice[str], motivo: str = None):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # 1. Registro na planilha
    try:
        sh.append_row([id_usuario, status.value, agora, motivo if motivo else "Nenhum"])
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro ao salvar na planilha: {e}", ephemeral=True)
        return
    
    # 2. Lógica de Banimento Condicional
    mensagem_extra = ""
    if motivo:
        try:
            member = await interaction.guild.fetch_member(int(id_usuario))
            await member.ban(reason=motivo)
            mensagem_extra = f"\n🔨 Usuário banido. Motivo: {motivo}"
        except Exception as e:
            mensagem_extra = f"\n⚠️ Falha ao banir (verifique o ID ou permissões): {e}"

    # 3. Resposta ao comando
    await interaction.response.send_message(f"✅ Usuário {id_usuario} registrado como **{status.value}**!{mensagem_extra}", ephemeral=True)

# 2. Token de segurança lido da variável de ambiente
token = os.environ.get("MTUxMTI5MDkzOTY2OTM1MjU0OA.GVQ3Fc.-1vT9XexuSVJBXiFB1vVAkRbD9hwkq0q3CrBcs")
bot.run(token)
