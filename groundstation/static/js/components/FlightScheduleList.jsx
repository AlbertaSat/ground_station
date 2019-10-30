import React from 'react'
import Paper from '@material-ui/core/Paper';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import AddIcon from '@material-ui/icons/Add';
import DeleteIcon from '@material-ui/icons/Delete';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

function isMinified(minify, elemt){
  if(!minify){
    return elmt
  }else{
    return
  }
}

const FlightScheduleList = (props) => {
	return (
       <div>
		<Paper className="grid-containers">
       	  <h5 className="container-text">Upcoming Flight Schedules</h5>
          {props.flightschedule.map((flightschedule, idx) => (
             <ExpansionPanel key={flightschedule.id}>
               <ExpansionPanelSummary
                 expandIcon={<ExpandMoreIcon style={{ color: '#4bacb8'}}/>}
                 aria-controls="panel1a-content"
                 id="panel1a-header"
               >
                  <Table aria-label="simple table">
                    <TableBody>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          {"Flight Schedule #" + flightschedule.id}
                        </TableCell>
                        <TableCell align="right">
                          {"Created at " + flightschedule.creationDate}
                        </TableCell>
                        {
                          !props.isMinified && 
                             <TableCell align="right">
                               <AddIcon 
                                 style={{ color: '#4bacb8', marginRight: '20px'}}
                                 onClick={ (event) => props.handleAddFlightOpenClick(event, idx) }
                               />
                               <DeleteIcon 
                                 style={{ color: '#4bacb8'}}
                                 onClick={ (event) => props.handleDeleteFlightOpenClick(event) }
                               />
                             </TableCell>
                        }
                      </TableRow>
                    </TableBody>
                  </Table>
                </ExpansionPanelSummary>
                <ExpansionPanelDetails>
                  <Table aria-label="simple table">
                      <TableHead>
                      	<TableRow>
                           <TableCell 
                      	      style={{backgroundColor: '#212529', color: '#fff', paddingTop: '8px', paddingBottom: '8px'}}>
                      		     ID
                      		</TableCell>
                      		<TableCell 
                            align="right"
                      		  style={{backgroundColor: '#212529', color: '#fff', paddingTop: '8px', paddingBottom: '8px'}}>
                      		    Command
                      		</TableCell>
                      		<TableCell 
                             align="right"
                      		   style={{backgroundColor: '#212529', color: '#fff', paddingTop: '8px', paddingBottom: '8px'}}>
                      		      Timestamp
                      		</TableCell>
                      	</TableRow>
                      </TableHead>
                    {flightschedule.commands.map(commands => (
                      <TableBody>
                        <TableRow>
                          <TableCell component ="th" scope="row">
                            {commands.commandId}
                          </TableCell>
                          <TableCell align="right">{commands.commandName}</TableCell>
                          <TableCell align="right">{commands.timeStamp}</TableCell>
                        </TableRow>
                      </TableBody>
                    ))} 
                   </Table>
                  </ExpansionPanelDetails>
                </ExpansionPanel>
              ))}
            </Paper>
          </div>
	)
}

export default FlightScheduleList;