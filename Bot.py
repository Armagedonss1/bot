import sqlite3 
import discord 
from discord.ext import commands 
from tabulate import tabulate 
import json 

conn = sqlite3.connect("Discord.db")
cursor = conn.cursor()

CREATE TABLE "Inventory" (
	"id"	INT,
	"type"	TEXT,
	"name"	TEXT,
	"cost"	INT
)

CREATE TABLE "Users" (
	"id"	INT,
	"nickname"	TEXT,
	"mention"	TEXT,
	"money"	INT,
	"rep_rank"	TEXT,
	"inventory"	TEXT,
	"lvl"	INT,
	"xp"	INT
)

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Bot Active")#сообщение о готовности
    for guild in bot.guilds:#т.к. бот для одного сервера, то и цикл выводит один сервер
        print(guild.id)#вывод id сервера
        serv=guild#без понятия зачем это
        for member in guild.members:#цикл, обрабатывающий список участников
            cursor.execute(f"SELECT id FROM Users where id={member.id}")#проверка, существует ли участник в БД
            if cursor.fetchone()==None:#Если не существует
                cursor.execute(f"INSERT INTO Users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 0, '10','[]',0,100)")#вводит все данные об участнике в БД
            else:#если существует
                pass
            conn.commit()#применение изменений в БД

@bot.event
async def on_member_join(member):
    cursor.execute(f"SELECT id FROM Users where id={member.id}")#все также, существует ли участник в БД
    if cursor.fetchone()==None:#Если не существует
        cursor.execute(f"INSERT INTO Users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 0, '10','[]',0,0)")#вводит все данные об участнике в БД
    else:#Если существует
        pass
    conn.commit()#применение изменений в БД

@bot.event
async def on_message(message):
    if len(message.content) > 15:#за каждое сообщение длиной > 15 символов...
        for row in cursor.execute(f"SELECT xp,lvl,money FROM Users where id={message.author.id}"):
            expi=row[0]+random.randint(5, 40)#к опыту добавляется случайное число
            cursor.execute(f'UPDATE Users SET xp={expi} where id={message.author.id}')
            lvch=expi/(row[1]*1000)
            print(int(lvch))
            lv=int(lvch)
            if row[1] < lv:#если текущий уровень меньше уровня, который был рассчитан формулой выше,...
                await message.channel.send(f'Новый уровень!')#то появляется уведомление...
                bal=1000*lv
                cursor.execute(f'UPDATE Users SET lvl={lv},money={bal} where id={message.author.id}')#и участник получает деньги
    await bot.process_commands(message)#Далее это будет необходимо для ctx команд
    conn.commit()#применение изменений в БД

@bot.command()
async def account(ctx): #команда _account (где "_", ваш префикс указаный в начале)
    table=[["nickname","money","lvl","xp"]]
    for row in cursor.execute(f"SELECT nickname,money,lvl,xp FROM Users where id={ctx.author.id}"):
        table.append([row[0],row[1],row[2],row[3]])
        await ctx.send(f">\n{tabulate(table)}")

@bot.command()
async def inventory(ctx):#команда _inventory (где "_", ваш префикс указаный в начале)

    counter=0
    for row in cursor.execute(f"SELECT inventory FROM Users where id={ctx.author.id}"):
        data=json.loads(row[0])
        table=[["id","type","name"]]
        for row in data:
            prt=row
            for row in cursor.execute(f"SELECT id,type,name FROM Inventory where id={prt}"):
                counter+=1
                table.append([row[0],row[1],row[2]])
                
                if counter==len(data):
                    await ctx.send(f'>\n{tabulate(table)}')


@bot.command()
async def shop(ctx):#команда _shop (где "_", ваш префикс указаный в начале)
    counter=0
    table=[["id","type","name","cost"]]
    for row in cursor.execute(f"SELECT id,type,name,cost FROM Inventory"):
        counter+=1
        table.append([row[0],row[1],row[2],row[3]])
        if counter==4:
            await ctx.send(f'>\n{tabulate(table)}')

async def buy(ctx, a: int):
    uid=ctx.author.id
    await ctx.send('Обработка... Если ответа не последует, указан неверный id предмета [buy {id}]')
    for row in cursor.execute(f"SELECT money FROM Users where id={uid}"):
        money = row[0]
        for row in cursor.execute(f"SELECT id,name,cost FROM Inventory where id={a}"):
            cost=row[2]
            if money >= cost:#если у вас достаточно денег,то...
                money -=cost
                await ctx.send(f'Вы приобрели "{row[1]}" за {row[2]}')
                
                for row in cursor.execute(f"SELECT inventory FROM users where id={uid}"):
                    data=json.loads(row[0])
                    data.append(a)
                    daed=json.dumps(data)
                    cursor.execute('UPDATE Users SET money=?,inventory = ? where id=?',(money,daed,uid))#добавляет предмет вам в инвентарь
                    pass
            if money < cost:#иначе сообщает о недостатке
                await ctx.send(f'Недостаточно средств')
                pass
    conn.commit()#применение изменений в БД

bot.run("OTMxMjIwMDk2NzI5MzU4MzY3.GUrwuL.Da427lrw5uSgyzanEZdSjiyOY9I6KOQgkUB3Wk")


