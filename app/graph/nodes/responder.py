"""
Nó de resposta – FAQ em prompt + fallback determinístico por título.
"""
import traceback
from loguru import logger
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import AgenteState
from app.core.llm import criar_llm

llm = criar_llm(temperature=0.0)

# FAQ em memória (lista de dicionários)
FAQ_ITEMS = [
    {"titulo": "Horário de funcionamento", "resposta": "O Centro Oftalmológico funciona de segunda a sexta-feira das 8h00 às 19h00, e aos sábados das 9h00 às 13h00. Encerra aos domingos e feriados."},
    {"titulo": "Marcação de consultas", "resposta": "Pode marcar consulta pelo telefone +351 210 123 456, pelo nosso site oficial em www.centrooftalmo.pt ou diretamente na receção. Recomenda-se marcação prévia com pelo menos 48h de antecedência. Para urgências, não é necessário agendamento."},
    {"titulo": "Documentos necessários para a consulta", "resposta": "Traga o seu cartão de cidadão, cartão de utente do SNS ou seguro de saúde, e exames oftalmológicos anteriores (se os tiver). Se usa óculos ou lentes de contacto, leve-os consigo."},
    {"titulo": "Aceitam seguros de saúde?", "resposta": "Sim, trabalhamos com a maioria dos seguros de saúde em Portugal, incluindo Multicare, AdvanceCare, Médis, Allianz, entre outros. Consulte-nos para confirmar se o seu seguro é aceite."},
    {"titulo": "Tempo médio de consulta", "resposta": "Uma consulta de rotina tem duração média de 30 a 45 minutos. Exames complementares podem aumentar esse tempo. A primeira consulta costuma ser mais demorada devido à avaliação inicial completa."},
    {"titulo": "Cancelamento ou reagendamento", "resposta": "Pode cancelar ou reagendar a sua consulta até 24h antes do horário marcado, sem qualquer custo. Cancelamentos tardios ou faltas podem ter uma taxa associada."},
    {"titulo": "Consulta de oftalmologia geral", "resposta": "Avaliação completa da saúde ocular, incluindo medição da acuidade visual, refração, tonometria (pressão ocular) e exame do fundo do olho. Adequada para todas as idades."},
    {"titulo": "Especialidades disponíveis", "resposta": "Dispomos de consultas de subespecialidade em retina, glaucoma, catarata, córnea, oftalmopediatria, estrabismo, oculoplástica e cirurgia refrativa."},
    {"titulo": "Cirurgia de catarata", "resposta": "Realizamos cirurgia de catarata por facoemulsificação com implante de lente intraocular. O procedimento é ambulatório e dura cerca de 20 minutos. A recuperação visual costuma ser rápida."},
    {"titulo": "Cirurgia refrativa (LASIK)", "resposta": "Correção de miopia, hipermetropia e astigmatismo através de laser excimer. A cirurgia é indolor e permite na maioria dos casos deixar de usar óculos ou lentes de contacto."},
    {"titulo": "Exames de diagnóstico", "resposta": "Realizamos tomografia de coerência ótica (OCT), campimetria computorizada (campo visual), topografia corneana, paquimetria, angiografia, ecografia ocular, entre outros."},
    {"titulo": "Contactos principais", "resposta": "Telefone: +351 210 123 456 | Email: info@centrooftalmo.pt | Morada: Avenida da Visão, 123, 1000-001 Lisboa, Portugal"},
    {"titulo": "Redes sociais", "resposta": "Pode seguir-nos no Facebook (facebook.com/centrooftalmo), Instagram (@centrooftalmo) e LinkedIn para novidades e dicas de saúde ocular."},
    {"titulo": "Como chegar", "resposta": "Estamos localizados na Av. da Visão, junto ao Metro da Visão (linha Azul). Dispomos de parque de estacionamento gratuito para clientes."},
    {"titulo": "Corpo clínico", "resposta": "A nossa equipa é liderada pelo Dr. João Silva (Diretor Clínico, especialista em retina), Dra. Maria Santos (especialista em glaucoma e catarata), Dra. Ana Costa (oftalmopediatria), Dr. Pedro Oliveira (córnea e cirurgia refrativa) e Dra. Sara Almeida (oculoplástica)."},
    {"titulo": "Diferenciação da equipa", "resposta": "Todos os nossos médicos têm formação em instituições de referência nacionais e internacionais, e participam regularmente em congressos e formações contínuas."},
    {"titulo": "O que é a catarata?", "resposta": "A catarata é a opacificação do cristalino, a lente natural do olho, que leva à diminuição progressiva da visão. É a principal causa de cegueira reversível no mundo e afeta sobretudo pessoas com mais de 60 anos."},
    {"titulo": "Sintomas da catarata", "resposta": "Os sintomas incluem visão turva ou enevoada, sensibilidade à luz (fotofobia), dificuldade para conduzir à noite, ver halos em volta das luzes, necessidade de luz mais forte para ler, alteração frequente da graduação dos óculos e cores desbotadas ou amareladas."},
    {"titulo": "Tratamento da catarata", "resposta": "O tratamento é cirúrgico. A cirurgia consiste na remoção do cristalino opaco e substituição por uma lente intraocular. É um procedimento seguro e eficaz. Não existem medicamentos ou colírios que eliminem a catarata."},
    {"titulo": "O que é o glaucoma?", "resposta": "O glaucoma é uma doença ocular crónica que danifica o nervo ótico, geralmente associada ao aumento da pressão intraocular. É uma das principais causas de cegueira irreversível no mundo. Pode ser assintomático nas fases iniciais."},
    {"titulo": "Tipos de glaucoma", "resposta": "Os principais tipos são: glaucoma de ângulo aberto (o mais comum, crónico), glaucoma de ângulo fechado (agudo, emergência médica), glaucoma congénito (presente ao nascimento) e glaucoma secundário (causado por outras doenças ou medicamentos)."},
    {"titulo": "Fatores de risco", "resposta": "Idade superior a 40 anos, história familiar de glaucoma, pressão intraocular elevada, miopia elevada, diabetes e hipertensão arterial são fatores de risco importantes para o desenvolvimento do glaucoma."},
    {"titulo": "O que é o astigmatismo?", "resposta": "O astigmatismo é um erro refrativo causado por uma curvatura irregular da córnea ou do cristalino, que faz com que a luz se foque em vários pontos da retina, provocando visão distorcida ou desfocada tanto para longe como para perto."},
    {"titulo": "Correção do astigmatismo", "resposta": "Pode ser corrigido com óculos de lentes cilíndricas, lentes de contacto tóricas ou cirurgia refrativa (LASIK, PRK). O tratamento depende do grau de astigmatismo e da espessura corneana."},
    {"titulo": "O que é a miopia?", "resposta": "A miopia é um erro refrativo em que a imagem se forma antes da retina, fazendo com que os objetos distantes fiquem desfocados, enquanto os próximos são vistos com clareza. Ocorre porque o globo ocular é mais alongado ou a córnea é muito curva."},
    {"titulo": "Progressão da miopia em crianças", "resposta": "A miopia pode progredir durante a infância e adolescência devido ao crescimento ocular. Atualmente existem estratégias para travar essa progressão, como lentes de desfoque periférico, colírios de atropina diluída e ortoceratologia."},
    {"titulo": "O que é a hipermetropia?", "resposta": "A hipermetropia é um erro refrativo em que a imagem se forma atrás da retina, causando dificuldade em ver objetos próximos. Em jovens, o cristalino pode compensar, mas com a idade essa capacidade diminui, tornando os sintomas mais evidentes."},
    {"titulo": "Tomografia de coerência ótica (OCT)", "resposta": "A OCT é um exame de imagem não invasivo que permite obter cortes transversais da retina e do nervo ótico com alta resolução. É fundamental no diagnóstico e seguimento de doenças como glaucoma, degenerescência macular e edema macular diabético."},
    {"titulo": "Campo visual", "resposta": "O exame de campo visual (campimetria) avalia a amplitude e sensibilidade da visão periférica. É essencial no diagnóstico e controlo do glaucoma e de algumas lesões neurológicas."},
    {"titulo": "Sinais de alarme", "resposta": "Deve procurar atendimento urgente se tiver perda súbita de visão, dor ocular intensa, trauma ocular, hemorragia no olho, flashes de luz repentinos acompanhados de moscas volantes (possível descolamento de retina) ou queimaduras químicas."},
    {"titulo": "O que fazer em caso de trauma ocular?", "resposta": "Em caso de trauma ocular, não esfregue nem aplique pressão sobre o olho. Se houver corpo estranho, não tente removê-lo. Cubra o olho com uma proteção rígida (ex: copo de papel) e dirija-se imediatamente a um serviço de urgência oftalmológica."},
    {"titulo": "Regra 20-20-20", "resposta": "Para reduzir a fadiga ocular ao usar ecrãs, siga a regra 20-20-20: a cada 20 minutos, olhe para algo a 20 pés (cerca de 6 metros) durante pelo menos 20 segundos. Pisque regularmente para manter os olhos lubrificados."},
    {"titulo": "Consulta regular", "resposta": "Recomenda-se uma consulta oftalmológica de rotina a cada 1-2 anos para adultos, e anualmente para crianças e idosos. Pessoas com diabetes, hipertensão ou histórico familiar de glaucoma devem fazer controlos mais frequentes."}
]

# Construir o prompt com a lista numerada
FAQ_LISTA = "\n".join([f"{i+1}. {item['titulo']}: {item['resposta']}" for i, item in enumerate(FAQ_ITEMS)])

SYSTEM_PROMPT = f"""És um assistente do Centro Oftalmológico. Usa APENAS a lista de FAQs abaixo.
Regras:
1. Identifica o título que melhor corresponde à pergunta do utilizador (semântica, não apenas palavras exatas).
2. Responde EXATAMENTE com a resposta correspondente, sem acrescentar nada.
3. Se não houver correspondência, diz: "Peço desculpa, mas não tenho informação suficiente para responder a essa questão."
4. Para saudações, responde cordialmente.

FAQs:
{FAQ_LISTA}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "Pergunta: {pergunta}")
])

# Palavras-chave para forçar correspondência direta (método determinístico)
KEYWORD_MAP = {
    "horário": "Horário de funcionamento",
    "funcionamento": "Horário de funcionamento",
    "aberto": "Horário de funcionamento",
    "marcação": "Marcação de consultas",
    "agendar": "Marcação de consultas",
    "documento": "Documentos necessários para a consulta",
    "seguro": "Aceitam seguros de saúde?",
    "tempo médio": "Tempo médio de consulta",
    "cancelar": "Cancelamento ou reagendamento",
    "reagendar": "Cancelamento ou reagendamento",
    "oftalmologia geral": "Consulta de oftalmologia geral",
    "especialidades": "Especialidades disponíveis",
    "catarata": "O que é a catarata?",
    "glaucoma": "O que é o glaucoma?",
    "astigmatismo": "O que é o astigmatismo?",
    "miopia": "O que é a miopia?",
    "hipermetropia": "O que é a hipermetropia?",
    "oct": "Tomografia de coerência ótica (OCT)",
    "campo visual": "Campo visual",
    "equipa": "Corpo clínico",
    "médicos": "Corpo clínico",
    "contacto": "Contactos principais",
    "telefone": "Contactos principais",
    "morada": "Como chegar",
    "localização": "Como chegar",
    "sinais alarme": "Sinais de alarme",
    "urgência": "Sinais de alarme",
    "trauma ocular": "O que fazer em caso de trauma ocular?",
    "fadiga ocular": "Regra 20-20-20",
    "consulta regular": "Consulta regular",
}

def match_deterministico(pergunta: str):
    """Se a pergunta contiver uma palavra-chave, devolve a resposta correspondente."""
    pergunta_lower = pergunta.lower()
    for chave, titulo in KEYWORD_MAP.items():
        if chave in pergunta_lower:
            for item in FAQ_ITEMS:
                if item["titulo"] == titulo:
                    return item["resposta"]
    return None

async def responder(state: AgenteState) -> AgenteState:
    pergunta = state["mensagem_reformulada"]
    try:
        # Tentar correspondência determinística primeiro
        resposta_deterministica = match_deterministico(pergunta)
        if resposta_deterministica:
            state["resposta_final"] = resposta_deterministica
            logger.info("Resposta determinística por palavra-chave")
            return state

        # Se não encontrou, usar a LLM
        resposta = await llm.ainvoke(prompt.format_messages(pergunta=pergunta))
        state["resposta_final"] = resposta.content.strip()
        logger.info("Resposta extraída do FAQ via LLM")
    except Exception as e:
        logger.error(f"Erro: {traceback.format_exc()}")
        state["resposta_final"] = "Ocorreu um erro ao processar a sua pergunta."
    return state